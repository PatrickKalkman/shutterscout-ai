from dotenv import load_dotenv
from loguru import logger

from shutterscout_ai.core.shutterscout_agent import get_location_recommendations


def main() -> None:
    """Main entry point for the ShutterScout AI application."""
    logger.info("Starting ShutterScout AI...")
    load_dotenv()
    logger.info("Environment variables loaded")

    try:
        logger.info("Getting photography location recommendations...")
        recommendations = get_location_recommendations()

        with open("photography_location_recommendations.md", "w") as f:
            f.write(recommendations)

        logger.info("\nPhotography Location Recommendations:")
        logger.info(recommendations)
    # test_tools()

    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")

    logger.info("ShutterScout AI stopped")


if __name__ == "__main__":
    main()
