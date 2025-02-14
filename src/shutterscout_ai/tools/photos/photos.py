import os
from enum import Enum
from typing import List, Optional, TypedDict

import requests
from loguru import logger
from smolagents import tool


class PhotoSize(str, Enum):
    SMALL_SQUARE = "s"  # 75x75
    LARGE_SQUARE = "q"  # 150x150
    THUMBNAIL = "t"  # 100 on longest side
    SMALL = "m"  # 240 on longest side
    MEDIUM = ""  # 500 on longest side
    LARGE = "b"  # 1024 on longest side
    LARGE_1600 = "h"  # 1600 on longest side
    LARGE_2048 = "k"  # 2048 on longest side


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


class PhotoUrl(TypedDict):
    id: str
    title: str
    url: str


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
            "sort": "relevance",  # Sort by relevance
            "per_page": 5,  # Limit to 5 photos
            "extras": "views,date_taken",  # Get additional metadata
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


@tool
def get_photo_urls(photos: List[FlickrPhoto], size: Optional[PhotoSize] = None) -> List[PhotoUrl]:
    """
    Convert Flickr photo data into actual photo URLs.

    Args:
        photos: List of Flickr photos from search_flickr_photos
        size: Optional photo size (default is medium 500px)
    """
    try:
        urls = []
        size_suffix = f"_{size.value}" if size and size.value else ""

        for photo in photos:
            url = (
                f"https://farm{photo['farm']}.staticflickr.com/"
                f"{photo['server']}/"
                f"{photo['id']}_{photo['secret']}"
                f"{size_suffix}.jpg"
            )
            urls.append({"id": photo["id"], "title": photo["title"], "url": url})

        return urls
    except (KeyError, TypeError) as e:
        logger.error(f"Invalid photo data format: {str(e)}")
        raise ValueError(f"Invalid photo data format: {str(e)}") from e
