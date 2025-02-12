from dataclasses import dataclass

import requests
from loguru import logger
from smolagents import tool


@dataclass
class SunTimes:
    """Class to hold sunrise and sunset times"""

    sunrise: str
    sunset: str
    day_length: str


@tool
def get_sunrise_sunset(latitude: float, longitude: float) -> SunTimes:
    """
    Get sunrise and sunset times for a given location using the sunrise-sunset.org API.
    Returns times in UTC.

    Args:
        latitude: The latitude of the location
        longitude: The longitude of the location
    """
    try:
        url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&date=today"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        
        if data.get("status") != "OK":
            logger.error(f"API returned error status: {data.get('status')}")
            raise ValueError(f"Sunrise-sunset API error: {data.get('status')}")

        results = data.get("results", {})
        
        return SunTimes(
            sunrise=results["sunrise"],
            sunset=results["sunset"],
            day_length=results["day_length"]
        )
    except requests.RequestException as e:
        logger.error(f"Failed to fetch sun times data: {str(e)}")
        raise RuntimeError(f"Failed to fetch sun times data: {str(e)}") from e
    except (KeyError, TypeError) as e:
        logger.error(f"Invalid sun times data received: {str(e)}")
        raise ValueError(f"Invalid sun times data received: {str(e)}") from e
