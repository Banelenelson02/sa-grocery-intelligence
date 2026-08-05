from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "banele",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="monthly_basket_dag",
    default_args=default_args,
    description="Load BusinessTech monthly basket comparison data",
    schedule_interval="0 9 1 * *",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["etl", "grocery", "monthly"],
) as dag:

    def load_businesstech_task(**context):
        from etl.extract.businesstech import BusinessTechParser
        from etl.transform.normalize import normalize_dataframe
        from etl.transform.clean import validate_prices
        from etl.load.postgres_loader import PostgresLoader
        import os

        csv_path = "data/raw/businesstech_basket_latest.csv"

        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"BusinessTech CSV not found at {csv_path}. "
                "Update it manually from businesstech.co.za"
            )

        parser = BusinessTechParser()
        df = parser.load(csv_path)
        print(f"Loaded {len(df)} rows from BusinessTech CSV")

        normalized = normalize_dataframe(df)
        report = validate_prices(normalized)

        print(f"Valid: {len(report.valid)} | Rejected: {len(report.rejected)}")

        loader = PostgresLoader()
        summary = loader.load(report.valid)
        summary["rejected"] = len(report.rejected)

        print(f"Monthly load complete: {summary}")
        return summary

    load_businesstech = PythonOperator(
        task_id="load_businesstech",
        python_callable=load_businesstech_task,
    )