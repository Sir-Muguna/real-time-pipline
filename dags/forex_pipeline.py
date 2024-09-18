from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import subprocess

# Default arguments for DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 18),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'forex_pipeline',
    default_args=default_args,
    description='A Kafka Forex Data Pipeline',
    schedule_interval=timedelta(minutes=10),  # Adjust schedule as needed
)

# Path to producer and consumer scripts
producer_script = "/root/projects/portfolio_projects/data_engineering/real-time-pipline/scripts/producer.py"
consumer_script = "/root/projects/portfolio_projects/data_engineering/real-time-pipline/scripts/consumer.py"

def run_producer():
    # Run the producer script
    subprocess.run(['python3', producer_script], check=True)

def run_consumer():
    # Run the consumer script
    subprocess.run(['python3', consumer_script], check=True)

# Define producer and consumer tasks
producer_task = PythonOperator(
    task_id='run_producer',
    python_callable=run_producer,
    dag=dag,
)

consumer_task = PythonOperator(
    task_id='run_consumer',
    python_callable=run_consumer,
    dag=dag,
)

# Set up task dependencies
producer_task >> consumer_task
