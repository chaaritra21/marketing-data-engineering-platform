import pendulum

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook


@dag(
    dag_id="marketing_warehouse_check",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["marketing", "postgres", "learning"],
    description="Checks the marketing PostgreSQL warehouse",
)
def marketing_warehouse_check():

    @task
    def check_warehouse():
        """Check that the marketing warehouse is accessible."""

        hook = PostgresHook(
            postgres_conn_id="marketing_postgres"
        )

        result = hook.get_first(
            """
            SELECT
                COUNT(*) AS fact_count
            FROM warehouse.fact_campaign_performance;
            """
        )

        fact_count = result[0]

        print(f"Warehouse fact rows: {fact_count}")

        if fact_count == 0:
            raise ValueError(
                "Warehouse fact table is empty"
            )

        print(
            "Marketing warehouse connection and data check passed."
        )

    check_warehouse()


marketing_warehouse_check()