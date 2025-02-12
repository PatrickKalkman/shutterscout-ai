from dataclasses import dataclass
import requests
from smolagents import tool


@dataclass
class SunTimes:
    """Class to hold sunrise and sunset times"""
    sunrise: str
    sunset: str
    day_length: str


@tool
def get_sun_times(latitude: float, longitude: float) -> SunTimes:
    """
    Get sunrise and sunset times for a given location using the sunrise-sunset.org API.
    Returns times in UTC.

    Args:
        latitude: The latitude of the location
        longitude: The longitude of the location
    """
    url = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&date=today"
    
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    results = data["results"]
    
    return SunTimes(
        sunrise=results["sunrise"],
        sunset=results["sunset"],
        day_length=results["day_length"]
    )
