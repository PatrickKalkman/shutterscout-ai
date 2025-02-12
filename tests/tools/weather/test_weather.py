from unittest.mock import patch, MagicMock
import os
import pytest
from shutterscout_ai.tools.weather import get_weather_forecast


@pytest.fixture
def mock_env_api_key(monkeypatch):
    """Fixture to set mock API key"""
    monkeypatch.setenv("TOMORROW_API_KEY", "test_api_key")


@pytest.fixture
def sample_weather_response():
    """Fixture providing sample weather API response"""
    return {
        "timelines": {
            "daily": [
                {
                    "time": "2025-02-12T05:00:00Z",
                    "values": {
                        "temperatureMin": 1.7,
                        "temperatureMax": 6.2,
                        "cloudCoverAvg": 93,
                        "precipitationProbabilityAvg": 1,
                        "visibilityAvg": 13.44,
                        "sunriseTime": "2025-02-12T06:59:00Z",
                        "sunsetTime": "2025-02-12T16:54:00Z",
                        "windSpeedAvg": 1.6,
                        "humidityAvg": 92,
                    }
                }
            ]
        }
    }


def test_get_weather_forecast_success(mock_env_api_key, sample_weather_response):
    """Test successful weather forecast retrieval"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = sample_weather_response
        mock_get.return_value = mock_response

        result = get_weather_forecast(51.9187, 4.364)

        assert len(result) == 1
        forecast = result[0]
        assert forecast["time"] == "2025-02-12T05:00:00Z"
        assert forecast["temperature_min"] == 1.7
        assert forecast["temperature_max"] == 6.2
        assert forecast["cloud_cover"] == 93
        assert forecast["precipitation_probability"] == 1
        assert forecast["visibility"] == 13.44
        assert forecast["sunrise_time"] == "2025-02-12T06:59:00Z"
        assert forecast["sunset_time"] == "2025-02-12T16:54:00Z"
        assert forecast["wind_speed"] == 1.6
        assert forecast["humidity"] == 92

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["location"] == "51.9187,4.364"
        assert kwargs["params"]["timesteps"] == "1d"
        assert kwargs["params"]["apikey"] == "test_api_key"


def test_get_weather_forecast_missing_api_key():
    """Test error handling when API key is missing"""
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="TOMORROW_API_KEY environment variable not set"):
            get_weather_forecast(51.9187, 4.364)


def test_get_weather_forecast_api_error(mock_env_api_key):
    """Test error handling when API request fails"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(RuntimeError, match="Failed to fetch weather forecast"):
            get_weather_forecast(51.9187, 4.364)


def test_get_weather_forecast_invalid_response(mock_env_api_key):
    """Test error handling when API returns invalid data"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "response"}
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="Invalid API response format"):
            get_weather_forecast(51.9187, 4.364)
