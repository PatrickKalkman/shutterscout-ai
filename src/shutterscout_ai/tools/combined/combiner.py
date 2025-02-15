from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from time import sleep
from typing import List, Optional, TypedDict

from loguru import logger
from smolagents import tool

from shutterscout_ai.tools.astronomy.astronomy import SunTimes, get_sunrise_sunset
from shutterscout_ai.tools.location.location import LocationInfo, get_location
from shutterscout_ai.tools.photos.photos import PhotoUrl, search_flickr_photos
from shutterscout_ai.tools.places.places import Place, get_interesting_places
from shutterscout_ai.tools.weather.weather import DailyWeather, get_weather_forecast


class CombinedData(TypedDict):
    """
    Type definition for combined data from all ShutterScout AI tools.

    Attributes:
        location (LocationInfo): Geographic location information including:
            - latitude (float): Location latitude
            - longitude (float): Location longitude
            - city (str): City name
            - region (str): Region/state name
            - country (str): Country name
            - timezone (str): Timezone identifier

        weather (List[DailyWeather]): 2-day weather forecast with daily data including:
            - time (str): ISO format timestamp
            - temperature_min (float): Minimum temperature in Celsius
            - temperature_max (float): Maximum temperature in Celsius
            - cloud_cover (int): Percentage of cloud cover (0-100)
            - precipitation_probability (int): Chance of precipitation (0-100)
            - visibility (float): Visibility distance in kilometers
            - sunrise_time (str): Local sunrise time
            - sunset_time (str): Local sunset time
            - wind_speed (float): Average wind speed in km/h
            - humidity (int): Relative humidity percentage (0-100)

        sun_times (SunTimes): Astronomical data including:
            - sunrise (str): Sunrise time in UTC
            - sunset (str): Sunset time in UTC
            - day_length (str): Length of daylight period

        places (List[Place]): Notable locations nearby including:
            - name (str): Place name
            - latitude (float): Place latitude
            - longitude (float): Place longitude

        photos_by_place (dict[str, List[PhotoUrl]]): Photos for each place:
            - Key: Place name (str)
            - Value: List of photos with:
                - id (str): Photo identifier
                - title (str): Photo title
                - url (str): Direct URL to photo
    """

    location: LocationInfo
    weather: List[DailyWeather]
    sun_times: SunTimes
    places: List[Place]
    photos_by_place: dict[str, List[PhotoUrl]]


def fetch_with_retry(func, *args, max_retries: int = 3, delay: float = 1.0) -> Optional[any]:
    """
    Helper function to retry API calls with exponential backoff.

    Args:
        func: Function to execute
        *args: Arguments to pass to the function
        max_retries: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)

    Returns:
        The function result if successful, None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            return func(*args)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"All retry attempts failed for {func.__name__}: {str(e)}")
                return None
            wait_time = delay * (2**attempt)
            logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {wait_time}s: {str(e)}")
            sleep(wait_time)
    return None


@tool
def get_combined_data(max_places: int = 5, photo_radius_km: int = 5) -> CombinedData:
    """
    Combines data from all ShutterScout AI tools into a single comprehensive response.
    Uses concurrent execution where possible to improve performance.

    This function aggregates location, weather, astronomical, and point-of-interest data
    along with relevant photos to provide a complete snapshot of a location's
    photography-relevant conditions and opportunities.

    Args:
        max_places: Maximum number of interesting places to fetch (default: 5)
        photo_radius_km: Radius in kilometers to search for photos around each place (default: 5)

    Returns:
        CombinedData: A TypedDict containing all aggregated information:
            - location: Geographic and timezone information
            - weather: 5-day weather forecast
            - sun_times: Sunrise/sunset times
            - places: List of interesting locations nearby
            - photos_by_place: Dictionary of photos for each place

    Raises:
        RuntimeError: If critical data (location, weather) cannot be fetched
        ValueError: If received data is invalid or incomplete

    Example:
        >>> data = get_combined_data(max_places=3, photo_radius_km=10)
        >>> print(f"Found {len(data['places'])} places in {data['location']['city']}")
        >>> for place in data['places']:
        ...     photos = data['photos_by_place'].get(place['name'], [])
        ...     print(f"{place['name']}: {len(photos)} photos available")

    Note:
        - The function implements retry logic for API calls to handle transient failures
        - Photos are fetched concurrently to minimize total execution time
        - Weather data includes 5 days of forecast with various meteorological parameters
        - Places are limited to avoid excessive API usage
        - All timestamps are in UTC unless otherwise specified
    """
    # Get location data first as it's required for other calls
    location = fetch_with_retry(get_location)

    # Prepare concurrent execution of weather and sun time fetching
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            "weather": executor.submit(
                fetch_with_retry, get_weather_forecast, location["latitude"], location["longitude"]
            ),
            "sun_times": executor.submit(
                fetch_with_retry, get_sunrise_sunset, location["latitude"], location["longitude"]
            ),
            "places": executor.submit(
                fetch_with_retry, get_interesting_places, location["latitude"], location["longitude"]
            ),
        }

        # Wait for all futures to complete
        results = {}
        for name, future in futures.items():
            try:
                result = future.result()
                if result is None:
                    raise RuntimeError(f"Failed to fetch {name} data")
                results[name] = result
            except Exception as e:
                logger.error(f"Error fetching {name}: {str(e)}")
                raise RuntimeError(f"Failed to fetch {name} data: {str(e)}") from e

    # Limit places and fetch photos concurrently
    places = results["places"][:max_places]
    photos_by_place = {}

    with ThreadPoolExecutor(max_workers=len(places)) as executor:
        photo_futures = {
            place["name"]: executor.submit(
                fetch_with_retry,
                search_flickr_photos,
                place["name"],
                place["latitude"],
                place["longitude"],
                photo_radius_km,
            )
            for place in places
        }

        # Collect photo results
        for place_name, future in photo_futures.items():
            try:
                photos = future.result()
                if photos:  # Only add if photos were found
                    photos_by_place[place_name] = photos
            except Exception as e:
                logger.warning(f"Failed to fetch photos for {place_name}: {str(e)}")
                continue

    # Convert SunTimes dataclass to dict if necessary
    sun_times_dict = (
        asdict(results["sun_times"]) if hasattr(results["sun_times"], "__dataclass_fields__") else results["sun_times"]
    )

    return {
        "location": location,
        "weather": results["weather"],
        "sun_times": sun_times_dict,
        "places": places,
        "photos_by_place": photos_by_place,
    }
