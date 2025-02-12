from unittest.mock import patch

import pytest

from shutterscout_ai.tools.location.location import get_location


@pytest.fixture
def mock_location_response():
    return {
        "ip": "213.93.94.134",
        "latitude": 51.9187,
        "longitude": 4.364,
        "city": "Vlaardingen",
        "region": "South Holland",
        "country_name": "The Netherlands",
        "timezone": "Europe/Amsterdam"
    }


def test_get_location_success(mock_location_response):
    """Test successful location retrieval with mocked response"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_location_response
        
        result = get_location()
        
        assert isinstance(result, dict)
        assert result["latitude"] == 51.9187
        assert result["longitude"] == 4.364
        assert result["city"] == "Vlaardingen"
        assert result["region"] == "South Holland"
        assert result["country"] == "The Netherlands"
        assert result["timezone"] == "Europe/Amsterdam"


def test_get_location_error():
    """Test handling of request failure"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API request failed")
        
        with pytest.raises(Exception):
            get_location()
