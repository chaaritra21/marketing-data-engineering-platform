import logging
import os

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


def create_audit_run() -> int:
    """Create a new audit record and return its run_id."""

    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO warehouse.etl_audit_log (
                    pipeline_name,
                    status
                )
                VALUES (
                    %s,
                    %s
                )
                RETURNING run_id;
                """,
                ("marketing_warehouse", "RUNNING"),
            )

            run_id = cursor.fetchone()[0]

        connection.commit()

        logging.info(
            "Created audit run: %d",
            run_id
        )

        return run_id

    finally:
        if connection:
            connection.close()


def mark_audit_success(
    run_id: int,
    customer_count: int,
    campaign_count: int,
    channel_count: int,
    date_count: int,
    fact_count: int,
):
    """Mark a pipeline run as successful."""

    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE warehouse.etl_audit_log
                SET
                    end_time = CURRENT_TIMESTAMP,
                    status = 'SUCCESS',
                    customer_count = %s,
                    campaign_count = %s,
                    channel_count = %s,
                    date_count = %s,
                    fact_count = %s
                WHERE run_id = %s;
                """,
                (
                    customer_count,
                    campaign_count,
                    channel_count,
                    date_count,
                    fact_count,
                    run_id,
                ),
            )

        connection.commit()

        logging.info(
            "Audit run %d marked SUCCESS",
            run_id
        )

    finally:
        if connection:
            connection.close()


def mark_audit_failed(
    run_id: int,
    error_message: str,
):
    """Mark a pipeline run as failed."""

    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE warehouse.etl_audit_log
                SET
                    end_time = CURRENT_TIMESTAMP,
                    status = 'FAILED',
                    error_message = %s
                WHERE run_id = %s;
                """,
                (
                    error_message[:5000],
                    run_id,
                ),
            )

        connection.commit()

        logging.info(
            "Audit run %d marked FAILED",
            run_id
        )

    finally:
        if connection:
            connection.close()