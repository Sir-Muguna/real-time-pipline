import json
from kafka import KafkaConsumer
from google.cloud import bigquery
import os
from datetime import datetime

# Set the environment variable for GCP authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/root/projects/portfolio_projects/data_engineering/real-time-pipline/gcp/service_account.json"

# Initialize BigQuery client
bq_client = bigquery.Client()

# Kafka consumer setup
consumer = KafkaConsumer(
    'forex_prices',  # Kafka topic name
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='forex_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# BigQuery table where data will be inserted
table_id = 'realtime-forex-pipeline.forex_data.forex_prices'

# Transformation function to process and clean data
def transform_data(data):
    def safe_float(value):
        try:
            return float(value) if value is not None else 0.0
        except ValueError:
            return 0.0
    
    return {
        'ticker': data.get('ticker', 'N/A'),
        'bid': safe_float(data.get('bid')),
        'ask': safe_float(data.get('ask')),
        'open': safe_float(data.get('open')),
        'low': safe_float(data.get('low')),
        'high': safe_float(data.get('high')),
        'changes': safe_float(data.get('changes')),
        'date': datetime.strptime(data.get('date', '1970-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S").isoformat()
    }

# Function to insert data into BigQuery
def insert_into_bigquery(data):
    # Convert datetime to ISO format string for BigQuery compatibility
    if 'date' in data and isinstance(data['date'], datetime):
        data['date'] = data['date'].isoformat()
    
    errors = bq_client.insert_rows_json(table_id, [data])  # Insert rows into BigQuery
    if errors == []:
        print(f"Successfully inserted {data}")
    else:
        print(f"Failed to insert data: {errors}")

# Consume messages from Kafka, transform them, and insert into BigQuery
try:
    for message in consumer:
        message_data = message.value
        print(f"Received data: {message_data}")
        
        # Transform the data
        transformed_data = transform_data(message_data)
        
        # Insert transformed data into BigQuery
        insert_into_bigquery(transformed_data)

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    consumer.close()
