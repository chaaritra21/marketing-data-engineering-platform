import pendulum
from datetime import timedelta

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook


@dag(
    dag_id="marketing_pipeline",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["marketing", "etl", "postgres"],
    description="Main marketing data engineering pipeline",
)
def marketing_pipeline():

    @task
    def start_pipeline():
        print("Starting marketing data pipeline")

    @task(
        retries=2,
        retry_delay=timedelta(minutes=1),
    )
    def check_warehouse():
        hook = PostgresHook(
            postgres_conn_id="marketing_postgres"
        )

        result = hook.get_first(
            """
            SELECT COUNT(*)
            FROM warehouse.fact_campaign_performance;
            """
        )

        fact_count = result[0]

        print(f"Fact rows available: {fact_count}")

        if fact_count == 0:
            raise ValueError("Fact table is empty")

    @task(
        retries=2,
        retry_delay=timedelta(minutes=1),
    )
    def run_quality_check():
        hook = PostgresHook(
            postgres_conn_id="marketing_postgres"
        )

        checks = {
            "customers": """
                SELECT COUNT(*)
                FROM warehouse.dim_customer;
            """,
            "campaigns": """
                SELECT COUNT(*)
                FROM warehouse.dim_campaign;
            """,
            "channels": """
                SELECT COUNT(*)
                FROM warehouse.dim_channel;
            """,
            "dates": """
                SELECT COUNT(*)
                FROM warehouse.dim_date;
            """,
            "facts": """
                SELECT COUNT(*)
                FROM warehouse.fact_campaign_performance;
            """,
        }

        results = {}

        for name, query in checks.items():
            result = hook.get_first(query)
            results[name] = result[0]

        print(f"Warehouse quality results: {results}")

        if results["customers"] == 0:
            raise ValueError("Customer dimension is empty")

        if results["campaigns"] == 0:
            raise ValueError("Campaign dimension is empty")

        if results["channels"] == 0:
            raise ValueError("Channel dimension is empty")

        if results["dates"] == 0:
            raise ValueError("Date dimension is empty")

        if results["facts"] == 0:
            raise ValueError("Fact table is empty")

        print("All warehouse quality checks passed")

    @task
    def finish_pipeline():
        print("Marketing data pipeline completed successfully")

    start = start_pipeline()
    warehouse = check_warehouse()
    quality = run_quality_check()
    finish = finish_pipeline()

    start >> warehouse >> quality >> finish


marketing_pipeline()