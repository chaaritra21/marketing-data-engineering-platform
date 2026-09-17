import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


RAW_DATA_PATH = Path("Data/Raw/posts.json")
PROCESSED_DATA_PATH = Path("Data/Processed/posts_processed.csv")


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def load_raw_data():
    """Load raw JSON data into a pandas DataFrame."""

    logging.info("Loading raw data from %s", RAW_DATA_PATH)

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw data file not found: {RAW_DATA_PATH}"
        )

    df = pd.read_json(RAW_DATA_PATH)

    logging.info("Loaded %d records", len(df))

    return df


def transform_data(df):
    """Clean and transform the raw dataset."""

    logging.info("Starting data transformation")

    required_columns = {"userId", "id", "title", "body"}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Standardize column names
    df.columns = [column.lower() for column in df.columns]

    # Remove duplicate records
    df = df.drop_duplicates()

    # Clean text fields
    df["title"] = df["title"].astype(str).str.strip()
    df["body"] = df["body"].astype(str).str.strip()

    # Create useful derived columns
    df["title_length"] = df["title"].str.len()
    df["body_length"] = df["body"].str.len()

    # Add processing timestamp
    df["processed_at"] = datetime.now(timezone.utc).isoformat()

    logging.info(
        "Transformation completed: %d records",
        len(df)
    )

    return df


def save_processed_data(df):
    """Save transformed data."""

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False
    )

    logging.info(
        "Processed data saved to %s",
        PROCESSED_DATA_PATH
    )


def main():
    """Run the transformation pipeline."""

    setup_logging()

    try:
        df = load_raw_data()
        df = transform_data(df)
        save_processed_data(df)

        logging.info(
            "Transformation pipeline completed successfully"
        )

    except Exception as error:
        logging.error(
            "Transformation pipeline failed: %s",
            error
        )
        raise


if __name__ == "__main__":
    main()