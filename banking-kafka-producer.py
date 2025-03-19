#!/usr/bin/env python3
"""
Banking Transaction Kafka Producer
This script reads banking transaction data from a CSV file and streams it to a Kafka topic,
simulating real-time API data.
"""

import json
import time
import pandas as pd
import random
from kafka import KafkaProducer
from datetime import datetime

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'banking-transactions'

# CSV file path - update this to your actual file path
CSV_FILE_PATH = 'banking_transactions.csv'

def create_producer():
    """Create and return a Kafka producer instance."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def load_data_from_csv():
    """Load banking transaction data from CSV file."""
    print(f"Loading data from {CSV_FILE_PATH}...")
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Successfully loaded {len(df)} records.")
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def send_transaction_to_kafka(producer, transaction):
    """Send a single transaction to Kafka topic."""
    # Add a timestamp for when the record was sent
    transaction['stream_timestamp'] = datetime.now().isoformat()
    
    # Convert any non-serializable values (like numpy types) to Python native types
    transaction_dict = {}
    for key, value in transaction.items():
        if pd.isna(value):
            transaction_dict[key] = None
        else:
            transaction_dict[key] = value
    
    # Send to Kafka
    producer.send(TOPIC_NAME, transaction_dict)
    return transaction_dict

def main():
    """Main function to stream banking transaction data to Kafka."""
    # Load the CSV data
    df = load_data_from_csv()
    if df is None:
        return
    
    # Convert DataFrame to list of dictionaries for easier processing
    transactions = df.to_dict('records')
    
    # Create Kafka producer
    producer = create_producer()
    
    try:
        print(f"Starting to stream banking transactions to topic {TOPIC_NAME}...")
        count = 0
        
        # Stream each transaction with a small delay to simulate real-time data
        for transaction in transactions:
            # Send transaction to Kafka
            sent_transaction = send_transaction_to_kafka(producer, transaction)
            
            # Print progress
            count += 1
            if count % 10 == 0:
                print(f"Sent {count} transactions. Latest: {transaction['fraud_bool']}")
            
            # Add a small random delay to simulate real-time streaming
            time.sleep(random.uniform(0.1, 0.5))
            
            # Optional: loop back to the beginning if you run out of data
            if count == len(transactions):
                print("Reached the end of the dataset. Starting over...")
                count = 0
                
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.flush()  # Ensure all messages are sent
        producer.close()
        print("Producer closed.")

if __name__ == "__main__":
    main()
