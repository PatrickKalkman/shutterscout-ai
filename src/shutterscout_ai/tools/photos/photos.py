import os
from typing import List, TypedDict

import requests
from loguru import logger
from smolagents import tool


class FlickrPhoto(TypedDict):
    id: str
    owner: str
    secret: str
    server: str
    farm: int
    title: str
    ispublic: int
    isfriend: int
    isfamily: int


class FlickrResponse(TypedDict):
    photos: dict
    stat: str


@tool
def search_flickr_photos(text: str, latitude: float, longitude: float, radius: int = 5) -> List[FlickrPhoto]:
    """
    Search for photos on Flickr based on text query and location.

    Args:
        text: Search text query
        latitude: Location latitude
        longitude: Location longitude
        radius: Search radius in km (default 5)
    """
    try:
        api_key = os.getenv("FLICKR_API_KEY")
        if not api_key:
            logger.error("FLICKR_API_KEY environment variable not set")
            raise ValueError("FLICKR_API_KEY environment variable not set")

        url = "https://www.flickr.com/services/rest/"
        params = {
            "method": "flickr.photos.search",
            "api_key": api_key,
            "text": text,
            "lat": latitude,
            "lon": longitude,
            "radius": radius,
            "format": "json",
            "nojsoncallback": 1,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data: FlickrResponse = response.json()

        if data.get("stat") != "ok":
            error_msg = data.get("message", "Unknown Flickr API error")
            logger.error(f"Flickr API returned error: {error_msg}")
            raise ValueError(f"Flickr API error: {error_msg}")

        return data["photos"]["photo"]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch photos from Flickr: {str(e)}")
        raise RuntimeError(f"Failed to fetch photos from Flickr: {str(e)}") from e
    except (KeyError, TypeError) as e:
        logger.error(f"Invalid photo data received from Flickr: {str(e)}")
        raise ValueError(f"Invalid photo data received from Flickr: {str(e)}") from e
