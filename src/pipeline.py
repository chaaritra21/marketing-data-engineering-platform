import logging
import time

from src.ingestion.api_ingestion import main as run_ingestion
from src.transformation.transform_posts import main as run_transformation
from src.warehouse.warehouse_loader import warehouse_setup
from src.warehouse.warehouse_quality import run_quality_checks


def setup_logging():
    """Configure application logging."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


def run_pipeline():
    """Run the complete data engineering pipeline."""

    pipeline_start = time.perf_counter()

    logging.info("=" * 70)
    logging.info("MARKETING DATA ENGINEERING PIPELINE STARTED")
    logging.info("=" * 70)

    try:

        # ------------------------------------------------------
        # 1. API INGESTION
        # ------------------------------------------------------

        logging.info("STEP 1/4 - Starting API ingestion")

        run_ingestion()

        logging.info(
            "STEP 1/4 - API ingestion completed successfully"
        )

        # ------------------------------------------------------
        # 2. TRANSFORMATION
        # ------------------------------------------------------

        logging.info(
            "STEP 2/4 - Starting data transformation"
        )

        run_transformation()

        logging.info(
            "STEP 2/4 - Data transformation completed successfully"
        )

        # ------------------------------------------------------
        # 3. WAREHOUSE LOAD
        # ------------------------------------------------------

        logging.info(
            "STEP 3/4 - Starting warehouse load"
        )

        warehouse_setup()

        logging.info(
            "STEP 3/4 - Warehouse load completed successfully"
        )

        # ------------------------------------------------------
        # 4. DATA QUALITY
        # ------------------------------------------------------

        logging.info(
            "STEP 4/4 - Starting warehouse quality checks"
        )

        quality_results = run_quality_checks()

        logging.info(
            "STEP 4/4 - Data quality checks completed successfully"
        )

        # ------------------------------------------------------
        # PIPELINE SUCCESS
        # ------------------------------------------------------

        elapsed_time = (
            time.perf_counter() - pipeline_start
        )

        logging.info("=" * 70)
        logging.info(
            "PIPELINE COMPLETED SUCCESSFULLY"
        )
        logging.info(
            "Quality results: %s",
            quality_results
        )
        logging.info(
            "Total execution time: %.2f seconds",
            elapsed_time
        )
        logging.info("=" * 70)

    except Exception as error:

        elapsed_time = (
            time.perf_counter() - pipeline_start
        )

        logging.error("=" * 70)
        logging.error(
            "PIPELINE FAILED"
        )
        logging.error(
            "Error: %s",
            error
        )
        logging.error(
            "Execution time before failure: %.2f seconds",
            elapsed_time
        )
        logging.error("=" * 70)

        raise


def main():
    setup_logging()
    run_pipeline()


if __name__ == "__main__":
    main()