from unittest.mock import patch

import pytest
from shutterscout_ai.tools.places.places import get_interesting_places


@pytest.fixture
def mock_response():
    return {
        "results": [
            {
                "fsq_id": "abc123",
                "name": "Test Museum",
                "categories": [{"id": 16019, "name": "Museum"}],
                "location": {
                    "address": "123 Test St",
                    "country": "US",
                    "formatted_address": "123 Test St, City, Country",
                    "locality": "City",
                    "postcode": "12345",
                },
                "distance": 500,
            }
        ]
    }


def test_get_interesting_places_success(mock_response):
    """Test successful retrieval of places"""
    with patch("requests.get") as mock_get, patch.dict(
        "os.environ", {"FOURSQUARE_API_KEY": "test-key"}
    ):
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None

        places = get_interesting_places(51.9187, 4.364)

        assert len(places) == 1
        assert places[0]["name"] == "Test Museum"
        assert places[0]["fsq_id"] == "abc123"
        assert places[0]["distance"] == 500

        # Verify API call parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["ll"] == "51.9187,4.364"
        assert kwargs["params"]["radius"] == 10000
        assert "16032" in kwargs["params"]["categories"]
        assert kwargs["headers"]["Authorization"] == "test-key"


def test_get_interesting_places_no_api_key():
    """Test error when API key is not set"""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="FOURSQUARE_API_KEY environment variable not set"):
            get_interesting_places(51.9187, 4.364)


def test_get_interesting_places_api_error():
    """Test handling of API errors"""
    with patch("requests.get") as mock_get, patch.dict(
        "os.environ", {"FOURSQUARE_API_KEY": "test-key"}
    ):
        mock_get.side_effect = Exception("API Error")

        with pytest.raises(RuntimeError, match="Failed to fetch places from Foursquare"):
            get_interesting_places(51.9187, 4.364)


def test_get_interesting_places_invalid_response():
    """Test handling of invalid API response"""
    with patch("requests.get") as mock_get, patch.dict(
        "os.environ", {"FOURSQUARE_API_KEY": "test-key"}
    ):
        mock_get.return_value.json.return_value = {"invalid": "response"}
        mock_get.return_value.raise_for_status.return_value = None

        # Should return empty list for missing 'results' key
        assert get_interesting_places(51.9187, 4.364) == []
