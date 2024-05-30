from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from google.cloud import bigquery
import pandas as pd
import os

data_dir = "/opt/airflow/data"


def extract_data():
    df = pd.read_csv(f"{data_dir}/data.csv")
    df.to_csv(f"{data_dir}/data_extracted.csv", index=False)
    print(os.listdir(data_dir))


def transform_data():
    df = pd.read_csv(f"{data_dir}/data_extracted.csv")
    df = df.dropna()
    df.to_csv(f"{data_dir}/data_transformed.csv", index=False)


def load_data():
    df = pd.read_csv(f"{data_dir}/data_transformed.csv")
    client = bigquery.Client()
    dataset_id = "ml_telemetry"
    table_id = "model_metrics"
    tableRef = client.dataset(dataset_id).table(table_id)
    print(df)
    # Logic to load data into BigQuery
    bigqueryJob = client.load_table_from_dataframe(df, tableRef)
    bigqueryJob.result()


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 5, 28),
    "retries": 1,
}

dag = DAG(
    "ml_model_monitoring",
    default_args=default_args,
    description="A simple DAG for ML model monitoring",
    schedule_interval="@daily",
)

t1 = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
    dag=dag,
)

t2 = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    dag=dag,
)

t3 = PythonOperator(
    task_id="load_data",
    python_callable=load_data,
    dag=dag,
)

t1 >> t2 >> t3
