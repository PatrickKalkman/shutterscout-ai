import os
from typing import TypedDict, List
from datetime import datetime

import requests
from loguru import logger
from smolagents import tool


class DailyWeather(TypedDict):
    """Type definition for daily weather information"""
    time: str
    temperature_min: float
    temperature_max: float
    cloud_cover: int
    precipitation_probability: int
    visibility: float
    sunrise_time: str
    sunset_time: str
    wind_speed: float
    humidity: int


@tool
def get_weather_forecast(latitude: float, longitude: float) -> List[DailyWeather]:
    """
    Retrieves a 5-day weather forecast for the specified location using Tomorrow.io API.
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        
    Returns:
        A list of daily weather forecasts containing temperature, cloud cover, precipitation probability,
        visibility, sunrise/sunset times, wind speed and humidity.
        
    Raises:
        RuntimeError: If the API request fails
        ValueError: If the API response is invalid or missing required data
    """
    api_key = os.getenv("TOMORROW_API_KEY")
    if not api_key:
        raise ValueError("TOMORROW_API_KEY environment variable not set")
        
    url = f"https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": f"{latitude},{longitude}",
        "timesteps": "1d",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "timelines" not in data or "daily" not in data["timelines"]:
            raise ValueError("Invalid API response format")
            
        forecasts = []
        for day in data["timelines"]["daily"]:
            forecast = DailyWeather(
                time=day["time"],
                temperature_min=day["values"]["temperatureMin"],
                temperature_max=day["values"]["temperatureMax"],
                cloud_cover=day["values"]["cloudCoverAvg"],
                precipitation_probability=day["values"]["precipitationProbabilityAvg"],
                visibility=day["values"]["visibilityAvg"],
                sunrise_time=day["values"]["sunriseTime"],
                sunset_time=day["values"]["sunsetTime"],
                wind_speed=day["values"]["windSpeedAvg"],
                humidity=day["values"]["humidityAvg"]
            )
            forecasts.append(forecast)
            
        return forecasts
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch weather forecast: {str(e)}")
        raise RuntimeError(f"Failed to fetch weather forecast: {str(e)}") from e
    except (KeyError, TypeError) as e:
        logger.error(f"Invalid weather data received: {str(e)}")
        raise ValueError(f"Invalid weather data received: {str(e)}") from e
