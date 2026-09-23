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


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def run_quality_checks():
    """Run warehouse-level data quality checks."""

    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)

        with connection.cursor() as cursor:

            # --------------------------------------------------
            # Check 1: Dimensions contain data
            # --------------------------------------------------

            cursor.execute(
                "SELECT COUNT(*) FROM warehouse.dim_customer"
            )
            customer_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM warehouse.dim_campaign"
            )
            campaign_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM warehouse.dim_channel"
            )
            channel_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM warehouse.dim_date"
            )
            date_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM warehouse.fact_campaign_performance
                """
            )
            fact_count = cursor.fetchone()[0]

            logging.info(
                "Row counts | customers=%d | campaigns=%d | "
                "channels=%d | dates=%d | facts=%d",
                customer_count,
                campaign_count,
                channel_count,
                date_count,
                fact_count,
            )

            if customer_count == 0:
                raise ValueError("Customer dimension is empty")

            if campaign_count == 0:
                raise ValueError("Campaign dimension is empty")

            if channel_count == 0:
                raise ValueError("Channel dimension is empty")

            if date_count == 0:
                raise ValueError("Date dimension is empty")

            if fact_count == 0:
                raise ValueError("Fact table is empty")

            # --------------------------------------------------
            # Check 2: No orphan customer keys
            # --------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM warehouse.fact_campaign_performance f
                LEFT JOIN warehouse.dim_customer c
                    ON f.customer_key = c.customer_key
                WHERE c.customer_key IS NULL
                """
            )

            orphan_customers = cursor.fetchone()[0]

            if orphan_customers > 0:
                raise ValueError(
                    f"Found {orphan_customers} orphan customer keys"
                )

            # --------------------------------------------------
            # Check 3: No orphan campaign keys
            # --------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM warehouse.fact_campaign_performance f
                LEFT JOIN warehouse.dim_campaign c
                    ON f.campaign_key = c.campaign_key
                WHERE c.campaign_key IS NULL
                """
            )

            orphan_campaigns = cursor.fetchone()[0]

            if orphan_campaigns > 0:
                raise ValueError(
                    f"Found {orphan_campaigns} orphan campaign keys"
                )

            # --------------------------------------------------
            # Check 4: Clicks cannot exceed impressions
            # --------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM warehouse.fact_campaign_performance
                WHERE clicks > impressions
                """
            )

            invalid_clicks = cursor.fetchone()[0]

            if invalid_clicks > 0:
                raise ValueError(
                    f"Found {invalid_clicks} rows where "
                    "clicks exceed impressions"
                )

            # --------------------------------------------------
            # Check 5: Conversions cannot exceed clicks
            # --------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM warehouse.fact_campaign_performance
                WHERE conversions > clicks
                """
            )

            invalid_conversions = cursor.fetchone()[0]

            if invalid_conversions > 0:
                raise ValueError(
                    f"Found {invalid_conversions} rows where "
                    "conversions exceed clicks"
                )

            # --------------------------------------------------
            # Check 6: Negative financial values
            # --------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM warehouse.fact_campaign_performance
                WHERE spend < 0
                   OR revenue < 0
                """
            )

            invalid_financials = cursor.fetchone()[0]

            if invalid_financials > 0:
                raise ValueError(
                    f"Found {invalid_financials} rows "
                    "with negative financial values"
                )

            logging.info(
                "All warehouse data quality checks passed"
            )

            return {
                "customers": customer_count,
                "campaigns": campaign_count,
                "channels": channel_count,
                "dates": date_count,
                "facts": fact_count,
            }

    finally:
        if connection:
            connection.close()


def main():
    setup_logging()

    logging.info(
        "Starting warehouse data quality checks"
    )

    results = run_quality_checks()

    logging.info(
        "Quality check summary: %s",
        results
    )

    logging.info(
        "Warehouse data quality pipeline completed successfully"
    )


if __name__ == "__main__":
    main()