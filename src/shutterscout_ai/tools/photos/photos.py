import os
from typing import List, TypedDict

import requests
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
    api_key = os.getenv("FLICKR_API_KEY")
    if not api_key:
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

    return data["photos"]["photo"]
