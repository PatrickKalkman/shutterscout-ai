import os
import pytest
from shutterscout_ai.tools.photos.photos import search_flickr_photos

def test_search_flickr_photos_missing_api_key():
    if "FLICKR_API_KEY" in os.environ:
        del os.environ["FLICKR_API_KEY"]
    
    with pytest.raises(ValueError, match="FLICKR_API_KEY environment variable not set"):
        search_flickr_photos("test", 51.9187, 4.364)

def test_search_flickr_photos_invalid_api_key(monkeypatch):
    monkeypatch.setenv("FLICKR_API_KEY", "invalid_key")
    
    with pytest.raises(requests.exceptions.HTTPError):
        search_flickr_photos("test", 51.9187, 4.364)
