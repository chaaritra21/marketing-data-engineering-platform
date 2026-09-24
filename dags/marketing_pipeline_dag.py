import os
import sys
import pendulum
from datetime import timedelta

from airflow.sdk import dag, task


PROJECT_DIR = "/opt/airflow/project"


@dag(
    dag_id="marketing_pipeline",
    schedule="30 0 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["marketing", "etl", "production"],
    description="Production-style marketing data engineering pipeline",
)
def marketing_pipeline():

    @task(
        retries=2,
        retry_delay=timedelta(minutes=1),
    )
    def api_ingestion():
        os.chdir(PROJECT_DIR)
        sys.path.insert(0, PROJECT_DIR)

        from src.ingestion.api_ingestion import main as run_ingestion

        print("Starting API ingestion...")
        run_ingestion()
        print("API ingestion completed successfully.")

    @task(
        retries=2,
        retry_delay=timedelta(minutes=1),
    )
    def transformation():
        os.chdir(PROJECT_DIR)
        sys.path.insert(0, PROJECT_DIR)

        from src.transformation.transform_posts import main as run_transformation

        print("Starting data transformation...")
        run_transformation()
        print("Data transformation completed successfully.")

    @task(
        retries=2,
        retry_delay=timedelta(minutes=1),
    )
    def warehouse_load():
        os.chdir(PROJECT_DIR)
        sys.path.insert(0, PROJECT_DIR)

        from src.warehouse.warehouse_loader import warehouse_setup

        print("Starting warehouse load...")
        warehouse_setup()
        print("Warehouse load completed successfully.")

    @task(
        retries=2,
        retry_delay=timedelta(minutes=1),
    )
    def data_quality():
        os.chdir(PROJECT_DIR)
        sys.path.insert(0, PROJECT_DIR)

        from src.warehouse.warehouse_quality import run_quality_checks

        print("Starting data quality checks...")

        results = run_quality_checks()

        print(f"Quality results: {results}")
        print("Data quality checks completed successfully.")

        return results

    @task(
        retries=1,
        retry_delay=timedelta(minutes=1),
    )
    def pipeline_monitoring(quality_results):
        run_time = pendulum.now("UTC")

        print("=" * 70)
        print("MARKETING PIPELINE MONITORING SUMMARY")
        print("=" * 70)

        print(f"Pipeline run time (UTC): {run_time}")

        print("Pipeline status: SUCCESS")

        print("Quality metrics:")

        if isinstance(quality_results, dict):
            for metric, value in quality_results.items():
                print(f"  {metric}: {value}")
        else:
            print(f"  Quality results: {quality_results}")

        print("Pipeline stages completed:")
        print("  API ingestion      : SUCCESS")
        print("  Transformation     : SUCCESS")
        print("  Warehouse load     : SUCCESS")
        print("  Data quality       : SUCCESS")

        print("=" * 70)
        print("MARKETING PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)

    ingestion = api_ingestion()
    transform = transformation()
    warehouse = warehouse_load()
    quality = data_quality()
    monitoring = pipeline_monitoring(quality)

    ingestion >> transform >> warehouse >> quality >> monitoring


marketing_pipeline()