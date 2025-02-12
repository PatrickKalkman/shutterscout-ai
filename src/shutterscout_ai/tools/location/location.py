from typing import TypedDict

import requests
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
    response = requests.get("https://ipapi.co/json/")
    data = response.json()

    return {
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "city": data["city"],
        "region": data["region"],
        "country": data["country_name"],
        "timezone": data["timezone"],
    }
