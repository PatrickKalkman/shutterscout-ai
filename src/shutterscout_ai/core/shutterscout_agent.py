from loguru import logger
from smolagents import CodeAgent, HfApiModel

from shutterscout_ai.tools.astronomy.astronomy import get_sunrise_sunset
from shutterscout_ai.tools.location.location import get_location
from shutterscout_ai.tools.photos.photos import search_flickr_photos
from shutterscout_ai.tools.places.places import get_interesting_places
from shutterscout_ai.tools.weather.weather import get_weather_forecast

SYSTEM_PROMPT = """You are ShutterScout AI, a photography location scout assistant. "
Your goal is to help photographers find great locations to shoot and determine the best time to photograph them.

Follow these steps to provide recommendations:
1. Get the user's location
2. Find interesting places nearby
3. Get weather forecasts for the area
4. Get sunrise/sunset times
5. Search for example photos of the locations

For each recommended location, provide:
- A brief description of the place
- Best time to photograph (based on sunrise/sunset and weather)
- Weather conditions to expect
- Example photos from other photographers
- Tips for shooting at this location

Focus on providing practical, actionable information that helps photographers plan their shoots."""


def create_shutterscout_agent(model_id: str = None) -> CodeAgent:
    """
    Create and configure a ShutterScout AI agent with all available tools.

    Args:
        model_id: Optional Hugging Face model ID. If not provided, will use the default model.

    Returns:
        Configured CodeAgent ready to provide photography location recommendations
    """
    try:
        # Initialize the model
        model = HfApiModel(model_id=model_id) if model_id else HfApiModel()

        # Create agent with all available tools
        tools = [
            get_location,
            get_weather_forecast,
            get_sunrise_sunset,
            get_interesting_places,
            search_flickr_photos,
        ]

        agent = CodeAgent(
            tools=tools,
            model=model,
            system_prompt=SYSTEM_PROMPT,
        )

        return agent

    except Exception as e:
        logger.error(f"Failed to create ShutterScout agent: {str(e)}")
        raise RuntimeError(f"Failed to create ShutterScout agent: {str(e)}") from e


def get_location_recommendations() -> str:
    """
    Get photography location recommendations using the ShutterScout AI agent.

    Returns:
        A formatted string containing location recommendations with weather and timing details.
    """
    try:
        agent = create_shutterscout_agent()

        prompt = """Analyze the current location and provide detailed recommendations
        for 2 interesting places to photograph.
        Include weather conditions, best time to shoot based on sunrise/sunset, and example photos.
        Format the response in a clear, easy-to-read way."""

        result = agent.run(prompt)
        return result

    except Exception as e:
        logger.error(f"Failed to get location recommendations: {str(e)}")
        raise RuntimeError(f"Failed to get location recommendations: {str(e)}") from e
