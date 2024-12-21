from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator

from download_data import download_data
from split_data import split_data
from data_to_minio import data_to_minio

dag = DAG(
    dag_id='movielens',
    start_date=datetime(2024, 12, 15),
    schedule_interval=None,
    catchup=False,
)

download_task = PythonOperator(
    task_id='download_data',
    python_callable=download_data,
    dag=dag,
)

split_task = PythonOperator(
    task_id='split',
    python_callable=split_data,
    dag=dag,
)

upload_task = PythonOperator(
    task_id='data_to_minio',
    python_callable=data_to_minio,
    dag=dag,
)

train_and_predict_task = BashOperator(
    task_id='train_predict',
    bash_command="spark-submit --jars /opt/apps/aws-java-sdk-bundle-1.12.540.jar,/opt/apps/hadoop-aws-3.3.4.jar /opt/apps/train_predict.py",
    dag=dag,
)

download_task >> split_task >> upload_task >> train_and_predict_task
