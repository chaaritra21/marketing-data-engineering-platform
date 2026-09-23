import logging
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

from src.warehouse.etl_audit import (
    create_audit_run,
    mark_audit_failed,
    mark_audit_success,
)

load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

CREATE_SQL_FILE = Path(
    "sql/warehouse/create_warehouse.sql"
)

LOAD_DIMENSIONS_SQL_FILE = Path(
    "sql/warehouse/load_dimensions.sql"
)

LOAD_FACT_SQL_FILE = Path(
    "sql/warehouse/load_fact.sql"
)


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

    return path.read_text(
        encoding="utf-8"
    )


def execute_sql(connection, sql: str):
    """Execute a SQL script."""

    with connection.cursor() as cursor:
        cursor.execute(sql)


def get_row_count(
    connection,
    table_name: str
) -> int:
    """Return row count for a warehouse table."""

    allowed_tables = {
        "dim_customer":
            "warehouse.dim_customer",

        "dim_campaign":
            "warehouse.dim_campaign",

        "dim_channel":
            "warehouse.dim_channel",

        "dim_date":
            "warehouse.dim_date",

        "fact_campaign_performance":
            "warehouse.fact_campaign_performance",
    }

    if table_name not in allowed_tables:
        raise ValueError(
            f"Invalid table requested: {table_name}"
        )

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {allowed_tables[table_name]}
            """
        )

        return cursor.fetchone()[0]


def get_warehouse_counts(connection):
    """Get all warehouse row counts."""

    return {
        "customers": get_row_count(
            connection,
            "dim_customer"
        ),
        "campaigns": get_row_count(
            connection,
            "dim_campaign"
        ),
        "channels": get_row_count(
            connection,
            "dim_channel"
        ),
        "dates": get_row_count(
            connection,
            "dim_date"
        ),
        "facts": get_row_count(
            connection,
            "fact_campaign_performance"
        ),
    }


def warehouse_setup():
    """Run the warehouse loading process."""

    connection = None
    run_id = create_audit_run()

    try:
        logging.info(
            "Starting warehouse pipeline | run_id=%d",
            run_id
        )

        connection = psycopg2.connect(**DB_CONFIG)

        logging.info(
            "Connected to PostgreSQL"
        )

        # ------------------------------------------------------
        # 1. CREATE TABLES
        # ------------------------------------------------------

        logging.info(
            "Creating warehouse tables"
        )

        create_sql = read_sql_file(
            CREATE_SQL_FILE
        )

        execute_sql(
            connection,
            create_sql
        )

        # ------------------------------------------------------
        # 2. LOAD DIMENSIONS
        # ------------------------------------------------------

        logging.info(
            "Loading warehouse dimensions"
        )

        dimensions_sql = read_sql_file(
            LOAD_DIMENSIONS_SQL_FILE
        )

        execute_sql(
            connection,
            dimensions_sql
        )

        # ------------------------------------------------------
        # 3. LOAD FACT
        # ------------------------------------------------------

        logging.info(
            "Loading campaign performance facts"
        )

        fact_sql = read_sql_file(
            LOAD_FACT_SQL_FILE
        )

        execute_sql(
            connection,
            fact_sql
        )

        # ------------------------------------------------------
        # 4. COMMIT
        # ------------------------------------------------------

        connection.commit()

        logging.info(
            "Warehouse data committed successfully"
        )

        # ------------------------------------------------------
        # 5. GET COUNTS
        # ------------------------------------------------------

        counts = get_warehouse_counts(
            connection
        )

        logging.info(
            "Warehouse row counts | "
            "customers=%d | "
            "campaigns=%d | "
            "channels=%d | "
            "dates=%d | "
            "facts=%d",
            counts["customers"],
            counts["campaigns"],
            counts["channels"],
            counts["dates"],
            counts["facts"],
        )

        # ------------------------------------------------------
        # 6. WRITE SUCCESS AUDIT
        # ------------------------------------------------------

        mark_audit_success(
            run_id=run_id,
            customer_count=counts["customers"],
            campaign_count=counts["campaigns"],
            channel_count=counts["channels"],
            date_count=counts["dates"],
            fact_count=counts["facts"],
        )

        logging.info(
            "Warehouse pipeline completed successfully"
        )

    except Exception as error:

        if connection:
            connection.rollback()

        logging.error(
            "Warehouse pipeline failed: %s",
            error
        )

        mark_audit_failed(
            run_id=run_id,
            error_message=str(error),
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

    warehouse_setup()


if __name__ == "__main__":
    main()