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
    dag_id="daily_prices_dag",
    default_args=default_args,
    description="Fetch SA grocery prices daily from Open Price Engine",
    schedule_interval="0 8 * * *",
    start_date=datetime(2026, 7, 7),
    catchup=False,
    tags=["etl", "grocery", "daily"],
) as dag:

    def extract_task(**context):
        from etl.extract.open_price_engine import OpenPriceEngineClient
        import pandas as pd
        import json

        client = OpenPriceEngineClient()
        products = ["bread", "milk", "eggs", "maize meal",
                    "sunflower oil", "butter", "rice", "sugar"]

        frames = []
        for product in products:
            try:
                df = client.fetch_prices(product=product)
                frames.append(df)
            except Exception as e:
                print(f"Warning: could not fetch {product}: {e}")

        if not frames:
            raise ValueError("No data extracted from OPE API")

        combined = pd.concat(frames, ignore_index=True)
        context["ti"].xcom_push(
            key="raw_rows",
            value=combined.to_json(date_format="iso")
        )
        print(f"Extracted {len(combined)} rows")
        return len(combined)

    def transform_task(**context):
        import pandas as pd
        from etl.transform.normalize import normalize_dataframe
        from etl.transform.clean import validate_prices
        import json

        raw_json = context["ti"].xcom_pull(
            key="raw_rows", task_ids="extract"
        )
        df = pd.read_json(raw_json)
        df["recorded_at"] = pd.to_datetime(df["recorded_at"], unit="ms")

        normalized = normalize_dataframe(df)
        report = validate_prices(normalized)

        print(f"Valid: {len(report.valid)} | Rejected: {len(report.rejected)}")
        for r in report.rejected:
            print(f"  Rejected: {r['reason']}")

        context["ti"].xcom_push(
            key="valid_rows",
            value=report.valid.to_json(date_format="iso")
        )
        return {"valid": len(report.valid), "rejected": len(report.rejected)}

    def load_task(**context):
        import pandas as pd
        from etl.load.postgres_loader import PostgresLoader

        valid_json = context["ti"].xcom_pull(
            key="valid_rows", task_ids="transform"
        )
        df = pd.read_json(valid_json)
        df["recorded_at"] = pd.to_datetime(df["recorded_at"], unit="ms")

        loader = PostgresLoader()
        summary = loader.load(df)
        print(f"Load complete: {summary}")
        return summary

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_task,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_task,
    )

    extract >> transform >> load