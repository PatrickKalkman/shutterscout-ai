from typing import TypedDict, List

from loguru import logger
from smolagents import tool

from shutterscout_ai.tools.astronomy.astronomy import get_sunrise_sunset, SunTimes
from shutterscout_ai.tools.location.location import get_location, LocationInfo
from shutterscout_ai.tools.photos.photos import search_flickr_photos, PhotoUrl
from shutterscout_ai.tools.places.places import get_interesting_places, Place
from shutterscout_ai.tools.weather.weather import get_weather_forecast, DailyWeather


class CombinedData(TypedDict):
    """Type definition for combined data from all tools"""
    location: LocationInfo
    weather: List[DailyWeather]
    sun_times: SunTimes
    places: List[Place]
    photos_by_place: dict[str, List[PhotoUrl]]


@tool
def get_combined_data() -> CombinedData:
    """
    Combines data from all ShutterScout AI tools into a single comprehensive response.
    
    Returns:
        A dictionary containing location info, weather forecast, astronomical data,
        interesting places, and related photos.
    
    Raises:
        RuntimeError: If any of the underlying API calls fail
        ValueError: If any of the received data is invalid
    """
    try:
        # Get location data
        location = get_location()
        
        # Get weather forecast
        weather = get_weather_forecast(location["latitude"], location["longitude"])
        
        # Get astronomical data
        sun_times = get_sunrise_sunset(location["latitude"], location["longitude"])
        
        # Get interesting places
        places = get_interesting_places(location["latitude"], location["longitude"])
        
        # Get photos for each place
        photos_by_place = {}
        for place in places[:2]:  # Limit to first 2 places to avoid too many API calls
            photos = search_flickr_photos(
                place["name"],
                latitude=place["latitude"],
                longitude=place["longitude"]
            )
            photos_by_place[place["name"]] = photos
        
        return {
            "location": location,
            "weather": weather,
            "sun_times": sun_times,
            "places": places,
            "photos_by_place": photos_by_place
        }
        
    except Exception as e:
        logger.error(f"Error combining tool data: {str(e)}")
        raise RuntimeError(f"Failed to combine tool data: {str(e)}") from e
