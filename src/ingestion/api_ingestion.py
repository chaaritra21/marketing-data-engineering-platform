import json
import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_URL = os.getenv("API_URL")

# Use the Data/Raw folder already present in your project
RAW_DATA_PATH = Path("Data/Raw/posts.json")


def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def extract_data():
    """Extract data from the API."""
    logging.info("Starting data extraction")

    if not API_URL:
        raise ValueError("API_URL is not configured in the .env file")

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    logging.info("Successfully extracted %d records", len(data))

    return data

def validate_data(data):
    """Validate the extracted API data."""

    if not isinstance(data, list):
        raise ValueError("Expected API response to be a list")

    if len(data) == 0:
        raise ValueError("API returned zero records")

    required_fields = {"userId", "id", "title", "body"}

    for record in data:
        if not required_fields.issubset(record.keys()):
            raise ValueError(
                f"Record is missing required fields: {required_fields}"
            )

    logging.info("Data validation successful: %d records", len(data))

def save_raw_data(data):
    """Save raw API response as JSON."""
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(RAW_DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    logging.info("Raw data saved to %s", RAW_DATA_PATH)


def main():
    """Run the ingestion pipeline."""
    setup_logging()

    try:
        data = extract_data()
        validate_data(data)
        save_raw_data(data)

        logging.info("Pipeline completed successfully")

    except Exception as error:
        logging.error("Pipeline failed: %s", error)
        raise


if __name__ == "__main__":
    main()