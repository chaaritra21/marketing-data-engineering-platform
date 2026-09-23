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
LOAD_DIMENSIONS_SQL_FILE = Path("sql/warehouse/load_dimensions.sql")
LOAD_FACT_SQL_FILE = Path("sql/warehouse/load_fact.sql")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def read_sql_file(path: Path) -> str:
    """Read SQL from a file."""

    if not path.exists():
        raise FileNotFoundError(
            f"SQL file not found: {path}"
        )

    return path.read_text(encoding="utf-8")


def execute_sql(connection, sql: str):
    """Execute a SQL script."""

    with connection.cursor() as cursor:
        cursor.execute(sql)


def get_row_count(connection, table_name: str) -> int:
    """Return row count for a warehouse table."""

    allowed_tables = {
        "dim_customer": "warehouse.dim_customer",
        "dim_campaign": "warehouse.dim_campaign",
        "dim_channel": "warehouse.dim_channel",
        "dim_date": "warehouse.dim_date",
        "fact_campaign_performance":
            "warehouse.fact_campaign_performance",
    }

    if table_name not in allowed_tables:
        raise ValueError(
            f"Invalid table requested: {table_name}"
        )

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT COUNT(*) FROM {allowed_tables[table_name]}"
        )
        return cursor.fetchone()[0]


def warehouse_setup():
    """Create warehouse tables and load warehouse data."""

    connection = None

    try:
        logging.info("Connecting to PostgreSQL")

        connection = psycopg2.connect(**DB_CONFIG)

        # ------------------------------------------------------
        # 1. CREATE TABLES
        # ------------------------------------------------------

        logging.info("Creating warehouse tables")

        create_sql = read_sql_file(CREATE_SQL_FILE)
        execute_sql(connection, create_sql)

        logging.info("Warehouse tables verified")

        # ------------------------------------------------------
        # 2. LOAD DIMENSIONS
        # ------------------------------------------------------

        logging.info("Loading warehouse dimensions")

        dimensions_sql = read_sql_file(
            LOAD_DIMENSIONS_SQL_FILE
        )

        execute_sql(connection, dimensions_sql)

        # ------------------------------------------------------
        # 3. LOAD FACT
        # ------------------------------------------------------

        logging.info("Loading campaign performance facts")

        fact_sql = read_sql_file(
            LOAD_FACT_SQL_FILE
        )

        execute_sql(connection, fact_sql)

        # Commit everything together
        connection.commit()

        logging.info("Warehouse data loaded successfully")

        # ------------------------------------------------------
        # 4. ROW COUNT VALIDATION
        # ------------------------------------------------------

        customer_count = get_row_count(
            connection,
            "dim_customer"
        )

        campaign_count = get_row_count(
            connection,
            "dim_campaign"
        )

        channel_count = get_row_count(
            connection,
            "dim_channel"
        )

        date_count = get_row_count(
            connection,
            "dim_date"
        )

        fact_count = get_row_count(
            connection,
            "fact_campaign_performance"
        )

        logging.info(
            "Warehouse row counts | "
            "customers=%d | "
            "campaigns=%d | "
            "channels=%d | "
            "dates=%d | "
            "facts=%d",
            customer_count,
            campaign_count,
            channel_count,
            date_count,
            fact_count
        )

    except Exception as error:

        if connection:
            connection.rollback()

        logging.error(
            "Warehouse pipeline failed: %s",
            error
        )

        raise

    finally:

        if connection:
            connection.close()

        logging.info(
            "PostgreSQL connection closed"
        )


def main():

    setup_logging()

    logging.info(
        "Starting warehouse pipeline"
    )

    warehouse_setup()

    logging.info(
        "Warehouse pipeline completed successfully"
    )


if __name__ == "__main__":
    main()