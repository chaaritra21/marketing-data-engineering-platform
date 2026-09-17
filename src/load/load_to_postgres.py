import logging
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

PROCESSED_DATA_PATH = Path("Data/Processed/posts_processed.csv")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def load_processed_data():
    """Read processed CSV data."""
    logging.info(
        "Loading processed data from %s",
        PROCESSED_DATA_PATH
    )

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed file not found: {PROCESSED_DATA_PATH}"
        )

    df = pd.read_csv(PROCESSED_DATA_PATH)

    logging.info("Loaded %d records", len(df))

    return df


def load_to_postgres(df):
    """Insert processed data into PostgreSQL."""

    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)

        cursor = connection.cursor()

        records = [
            (
                int(row["userid"]),
                int(row["id"]),
                row["title"],
                row["body"],
                int(row["title_length"]),
                int(row["body_length"]),
                row["processed_at"],
            )
            for _, row in df.iterrows()
        ]

        insert_query = """
            INSERT INTO marketing.posts
            (
                user_id,
                post_id,
                title,
                body,
                title_length,
                body_length,
                processed_at
            )
            VALUES %s
            ON CONFLICT (post_id)
            DO UPDATE SET
                title = EXCLUDED.title,
                body = EXCLUDED.body,
                title_length = EXCLUDED.title_length,
                body_length = EXCLUDED.body_length,
                processed_at = EXCLUDED.processed_at;
        """

        execute_values(
            cursor,
            insert_query,
            records
        )

        connection.commit()

        logging.info(
            "Successfully loaded %d records into PostgreSQL",
            len(records)
        )

    except Exception as error:
        if connection:
            connection.rollback()

        logging.error(
            "PostgreSQL load failed: %s",
            error
        )

        raise

    finally:
        if connection:
            connection.close()


def main():
    """Run the PostgreSQL loading pipeline."""

    setup_logging()

    df = load_processed_data()
    load_to_postgres(df)

    logging.info(
        "PostgreSQL loading pipeline completed successfully"
    )


if __name__ == "__main__":
    main()