import os

import pytest

from shutterscout_ai.tools.photos.photos import PhotoSize, get_photo_urls, search_flickr_photos


def test_search_flickr_photos_missing_api_key():
    if "FLICKR_API_KEY" in os.environ:
        del os.environ["FLICKR_API_KEY"]

    with pytest.raises(ValueError, match="FLICKR_API_KEY environment variable not set"):
        search_flickr_photos("test", 51.9187, 4.364)


def test_search_flickr_photos_invalid_api_key(monkeypatch):
    monkeypatch.setenv("FLICKR_API_KEY", "invalid_key")

    with pytest.raises(ValueError, match="Flickr API error: Invalid API Key"):
        search_flickr_photos("test", 51.9187, 4.364)


def test_get_photo_urls():
    sample_photos = [
        {
            "id": "123",
            "owner": "456",
            "secret": "abc",
            "server": "789",
            "farm": 66,
            "title": "Test Photo",
            "ispublic": 1,
            "isfriend": 0,
            "isfamily": 0,
        }
    ]

    urls = get_photo_urls(sample_photos)
    assert len(urls) == 1
    assert urls[0]["id"] == "123"
    assert urls[0]["title"] == "Test Photo"
    assert urls[0]["url"] == "https://farm66.staticflickr.com/789/123_abc.jpg"


def test_get_photo_urls_with_size():
    sample_photos = [
        {
            "id": "123",
            "owner": "456",
            "secret": "abc",
            "server": "789",
            "farm": 66,
            "title": "Test Photo",
            "ispublic": 1,
            "isfriend": 0,
            "isfamily": 0,
        }
    ]

    urls = get_photo_urls(sample_photos, PhotoSize.LARGE_SQUARE)
    assert len(urls) == 1
    assert urls[0]["url"] == "https://farm66.staticflickr.com/789/123_abc_q.jpg"
