from unittest.mock import patch
import pytest
from shutterscout_ai.tools.astronomy.astronomy import get_sun_times, SunTimes


@pytest.fixture
def mock_sun_response():
    return {
        "results": {
            "sunrise": "7:00:00 AM",
            "sunset": "7:00:00 PM",
            "day_length": "12:00:00"
        },
        "status": "OK"
    }


def test_get_sun_times(mock_sun_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_sun_response
        mock_get.return_value.raise_for_status.return_value = None
        
        result = get_sun_times(51.9187, 4.364)
        
        assert isinstance(result, SunTimes)
        assert result.sunrise == "7:00:00 AM"
        assert result.sunset == "7:00:00 PM"
        assert result.day_length == "12:00:00"
        
        mock_get.assert_called_once_with(
            "https://api.sunrise-sunset.org/json?lat=51.9187&lng=4.364&date=today"
        )


def test_get_sun_times_error():
    with patch('requests.get') as mock_get:
        mock_get.return_value.raise_for_status.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            get_sun_times(51.9187, 4.364)
