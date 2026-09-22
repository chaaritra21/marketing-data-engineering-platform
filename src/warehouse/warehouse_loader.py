import logging
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

SQL_FILE = Path("sql/warehouse/create_warehouse.sql")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def execute_sql_file():
    """Execute the warehouse DDL SQL file."""

    if not SQL_FILE.exists():
        raise FileNotFoundError(
            f"SQL file not found: {SQL_FILE}"
        )

    logging.info(
        "Loading SQL from %s",
        SQL_FILE
    )

    sql = SQL_FILE.read_text(encoding="utf-8")

    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)

        with connection.cursor() as cursor:
            cursor.execute(sql)

        connection.commit()

        logging.info(
            "Warehouse tables created successfully"
        )

    except Exception as error:
        if connection:
            connection.rollback()

        logging.error(
            "Warehouse setup failed: %s",
            error
        )

        raise

    finally:
        if connection:
            connection.close()


def main():
    setup_logging()
    execute_sql_file()

    logging.info(
        "Warehouse setup completed successfully"
    )


if __name__ == "__main__":
    main()