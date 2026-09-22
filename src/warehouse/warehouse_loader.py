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

CREATE_SQL_FILE = Path("sql/warehouse/create_warehouse.sql")
LOAD_SQL_FILE = Path("sql/warehouse/load_dimensions.sql")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def read_sql_file(path: Path) -> str:
    """Read SQL from a file."""

    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")

    return path.read_text(encoding="utf-8")


def execute_sql(connection, sql: str):
    """Execute a SQL script."""

    with connection.cursor() as cursor:
        cursor.execute(sql)


def warehouse_setup():
    """Create warehouse tables and load dimensions."""

    connection = None

    try:
        logging.info("Connecting to PostgreSQL")

        connection = psycopg2.connect(**DB_CONFIG)

        logging.info("Creating warehouse tables")

        create_sql = read_sql_file(CREATE_SQL_FILE)
        execute_sql(connection, create_sql)

        logging.info("Warehouse tables verified")

        logging.info("Loading warehouse dimensions")

        load_sql = read_sql_file(LOAD_SQL_FILE)
        execute_sql(connection, load_sql)

        connection.commit()

        logging.info("Warehouse dimensions loaded successfully")

    except Exception as error:
        if connection:
            connection.rollback()

        logging.error("Warehouse pipeline failed: %s", error)
        raise

    finally:
        if connection:
            connection.close()

        logging.info("PostgreSQL connection closed")


def main():
    setup_logging()

    logging.info("Starting warehouse pipeline")

    warehouse_setup()

    logging.info("Warehouse pipeline completed successfully")


if __name__ == "__main__":
    main()