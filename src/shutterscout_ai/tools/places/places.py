import os
from typing import List, TypedDict

import requests
from loguru import logger
from smolagents import tool


class Place(TypedDict):
    """Represents a simplified place with basic location information"""

    name: str
    latitude: float
    longitude: float


@tool
def get_interesting_places(latitude: float, longitude: float, radius: int = 10000) -> List[Place]:
    """
    Get interesting places around a location using Foursquare API, returning simplified location data.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        radius: Search radius in meters (default 10000)

    Returns:
        List of places with name and coordinates
    """
    api_key = os.getenv("FOURSQUARE_API_KEY")
    if not api_key:
        logger.error("FOURSQUARE_API_KEY environment variable not set")
        raise ValueError("FOURSQUARE_API_KEY environment variable not set")

    try:
        # Categories: landmarks, cultural spots, museums, entertainment, scenic lookouts
        categories = "16032,16015,16019,13003,10027"

        url = "https://api.foursquare.com/v3/places/search"
        headers = {"Authorization": api_key, "accept": "application/json"}
        params = {"ll": f"{latitude},{longitude}", "radius": radius, "categories": categories}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for place in data.get("results", []):
            try:
                location = {
                    "name": place["name"],
                    "latitude": place["geocodes"]["main"]["latitude"],
                    "longitude": place["geocodes"]["main"]["longitude"],
                }
                results.append(location)
            except (KeyError, TypeError) as e:
                logger.warning(f"Skipping place due to missing data: {str(e)}")
                continue
        return results
    except (requests.RequestException, Exception) as e:
        logger.error(f"Failed to fetch places from Foursquare: {str(e)}")
        raise RuntimeError(f"Failed to fetch places from Foursquare: {str(e)}") from e
    except (KeyError, TypeError) as e:
        logger.error(f"Invalid place data received from Foursquare: {str(e)}")
        raise ValueError(f"Invalid place data received from Foursquare: {str(e)}") from e
