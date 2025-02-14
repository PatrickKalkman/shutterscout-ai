from typing import TypedDict

import requests
from loguru import logger
from smolagents import tool


class LocationInfo(TypedDict):
    """Type definition for location information returned by the API"""

    latitude: float
    longitude: float
    city: str
    region: str
    country: str
    timezone: str


@tool
def get_location() -> LocationInfo:
    """
    Retrieves the user's location information based on their IP address using ipapi.co.
    Returns a dictionary containing latitude, longitude, city, region, country and timezone.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get("https://ipapi.co/json/", headers=headers)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            logger.error(f"API returned error: {data['error']}")
            raise ValueError(f"Location API error: {data['error']}")

        return {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "city": data["city"],
            "region": data["region"],
            "country": data["country_name"],
            "timezone": data["timezone"],
        }
    except requests.RequestException as e:
        logger.error(f"Failed to fetch location data: {str(e)}")
        raise RuntimeError(f"Failed to fetch location data: {str(e)}") from e
    except (KeyError, TypeError) as e:
        logger.error(f"Invalid location data received: {str(e)}")
        raise ValueError(f"Invalid location data received: {str(e)}") from e
