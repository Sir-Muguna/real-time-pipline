import requests
import json
from kafka import KafkaProducer
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# API key and URL
api_key = os.getenv('API_KEY')
api_url = f"https://financialmodelingprep.com/api/v3/fx?apikey={api_key}"

# Kafka producer setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092', 
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Kafka topic to stream the data to
topic_name = 'forex_prices'

# Exponential backoff parameters
backoff_time = 10  # Start with 10 seconds

try:
    while True:
        response = requests.get(api_url)
        
        # Check if the response was successful
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                # Prepare the data to send to Kafka
                forex_data = {
                    'ticker': entry.get('ticker', 'N/A'),
                    'bid': entry.get('bid', 'N/A'),
                    'ask': entry.get('ask', 'N/A'),
                    'open': entry.get('open', 'N/A'),
                    'low': entry.get('low', 'N/A'),
                    'high': entry.get('high', 'N/A'),
                    'changes': entry.get('changes', 'N/A'),
                    'date': entry.get('date', 'N/A')
                }
                # Send the data to the Kafka topic
                producer.send(topic_name, forex_data)
                print(f"Sent data: {forex_data}")
            
            # Reset backoff time on successful request
            backoff_time = 10

            # Simulate streaming with a delay
            time.sleep(10)  # Fetch data every 10 seconds
        
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            # Retry with exponential backoff
            print(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
            backoff_time = min(backoff_time * 2, 300)  # Exponential backoff, max 5 minutes

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    producer.close()
