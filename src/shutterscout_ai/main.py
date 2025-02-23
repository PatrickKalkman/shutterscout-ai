import argparse
import sys

from dotenv import load_dotenv
from loguru import logger

from shutterscout_ai.core.shutterscout_agent import get_location_recommendations
from shutterscout_ai.tools.astronomy.astronomy import get_sunrise_sunset
from shutterscout_ai.tools.location.location import get_location
from shutterscout_ai.tools.photos.photos import search_flickr_photos
from shutterscout_ai.tools.places.places import get_interesting_places
from shutterscout_ai.tools.weather.weather import get_weather_forecast


def test_tools() -> None:
    """Test all ShutterScout AI tools in sequence."""
    try:
        # 1. Get location
        logger.info("Getting location...")
        location = get_location()
        logger.info(f"Location: {location}")

        # 2. Get weather forecast
        logger.info("\nGetting weather forecast...")
        weather = get_weather_forecast(location["latitude"], location["longitude"])
        logger.info(f"Weather forecast: {weather}")

        # 3. Get sunrise/sunset times
        logger.info("\nGetting sunrise/sunset times...")
        sun_times = get_sunrise_sunset(location["latitude"], location["longitude"])
        logger.info(f"Sun times: {sun_times}")

        # 4. Get interesting places
        logger.info("\nGetting interesting places...")
        places = get_interesting_places(location["latitude"], location["longitude"])
        logger.info(f"Found {len(places)} interesting places")

        # 5. Search for photos near interesting places
        logger.info("\nSearching for photos...")
        for place in places[:2]:  # Limit to first 2 places to avoid too many API calls
            logger.info(f"\nSearching photos for: {place['name']}")
            # Use the original location coordinates since place location doesn't include lat/long
            photos = search_flickr_photos(place["name"], latitude=location["latitude"], longitude=location["longitude"])
            logger.info(f"Found {len(photos)} photos for {place['name']}:")
            for photo in photos:
                logger.info(f"- {photo['title']}: {photo['url']}")

    except Exception as e:
        logger.error(f"Error during tool testing: {str(e)}")


def main() -> None:
    """Main entry point for the ShutterScout AI application."""
    parser = argparse.ArgumentParser(description="ShutterScout AI - Photography Location Scout")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose (debug) output")
    parser.add_argument(
        "--output",
        default="photography_location_recommendations.md",
        help="Output file path for recommendations (default: photography_location_recommendations.md)",
    )
    args = parser.parse_args()

    # Configure logger
    logger.remove()  # Remove default handler
    log_level = "DEBUG" if args.verbose else "INFO"
    logger.add(sys.stderr, level=log_level)

    logger.info("Starting ShutterScout AI...")
    load_dotenv()
    logger.debug("Environment variables loaded")

    # test_tools()
    try:
        logger.info("Getting photography location recommendations...")
        recommendations = get_location_recommendations()

        with open(args.output, "w") as f:
            f.write(recommendations)

        logger.info("\nPhotography Location Recommendations:")
        logger.info(recommendations)

    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")

    logger.info("ShutterScout AI stopped")


if __name__ == "__main__":
    main()
