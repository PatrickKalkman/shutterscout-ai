from dotenv import load_dotenv
from loguru import logger


def main() -> None:
    """Main entry point for the ShutterScout AI application."""
    logger.info("Starting ShutterScout AI...")
    load_dotenv()
    logger.info("Environment variables loaded")
    logger.info("ShutterScout AI stopped")


if __name__ == "__main__":
    main()
