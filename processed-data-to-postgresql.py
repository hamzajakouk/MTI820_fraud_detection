#!/usr/bin/env python3
"""
Processed Data to PostgreSQL Connector
This script consumes processed banking transaction data from Kafka and stores it in PostgreSQL.
"""

import json
import time
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'processed-transactions'
CONSUMER_GROUP_ID = 'postgres-connector-group'

# PostgreSQL configuration
PG_HOST = 'localhost'
PG_PORT = 5432
PG_DATABASE = 'banking'
PG_USER = 'postgres'
PG_PASSWORD = 'postgres'  # Change this to your actual password

def create_kafka_consumer():
    """Create and return a Kafka consumer instance."""
    return KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        group_id=CONSUMER_GROUP_ID,
        enable_auto_commit=True
    )

def connect_to_postgres():
    """Connect to PostgreSQL and return the connection."""
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD
    )
    return conn

def create_table_if_not_exists(conn):
    """Create the table if it doesn't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS banking_transactions (
        id SERIAL PRIMARY KEY,
        fraud_bool INTEGER,
        income FLOAT,
        customer_age INTEGER,
        intended_balcon_amount FLOAT,
        payment_type VARCHAR(50),
        employment_status VARCHAR(50),
        credit_risk_score INTEGER,
        housing_status VARCHAR(50),
        risk_category VARCHAR(10),
        fraud_probability FLOAT,
        stream_timestamp TIMESTAMP,
        spark_processing_timestamp TIMESTAMP,
        pg_insertion_timestamp TIMESTAMP
    );
    """
    with conn.cursor() as cursor:
        cursor.execute(create_table_query)
    conn.commit()

def insert_transactions(conn, transactions):
    """Insert multiple transactions into PostgreSQL using batch execution."""
    insert_query = """
    INSERT INTO banking_transactions (
        fraud_bool, income, customer_age, intended_balcon_amount,
        payment_type, employment_status, credit_risk_score, housing_status,
        risk_category, fraud_probability, stream_timestamp, spark_processing_timestamp,
        pg_insertion_timestamp
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    # Prepare data for batch insertion
    pg_insertion_timestamp = datetime.now()
    data = []
    
    for transaction in transactions:
        # Parse timestamps or use None if missing
        try:
            stream_ts = datetime.fromisoformat(transaction.get('stream_timestamp', ''))
        except (ValueError, TypeError):
            stream_ts = None
            
        try:
            spark_ts = datetime.fromisoformat(transaction.get('spark_processing_timestamp', ''))
        except (ValueError, TypeError):
            spark_ts = None
        
        # Extract only the fields we need
        row = (
            transaction.get('fraud_bool'),
            transaction.get('income'),
            transaction.get('customer_age'),
            transaction.get('intended_balcon_amount'),
            transaction.get('payment_type'),
            transaction.get('employment_status'),
            transaction.get('credit_risk_score'),
            transaction.get('housing_status'),
            transaction.get('risk_category'),
            transaction.get('fraud_probability'),
            stream_ts,
            spark_ts,
            pg_insertion_timestamp
        )
        data.append(row)
    
    # Execute batch insert
    with conn.cursor() as cursor:
        execute_batch(cursor, insert_query, data)
    conn.commit()
    
    return len(data)

def main():
    """Main function to consume from Kafka and write to PostgreSQL."""
    print(f"Starting Processed Data to PostgreSQL connector for topic {TOPIC_NAME}...")
    
    # Create consumer
    consumer = create_kafka_consumer()
    
    # Connect to PostgreSQL
    conn = connect_to_postgres()
    
    try:
        # Create table if it doesn't exist
        create_table_if_not_exists(conn)
        print("Ensured PostgreSQL table exists")
        
        # Process counter and batch variables
        count = 0
        batch_start_time = time.time()
        batch_size = 100
        transaction_batch = []
        
        for message in consumer:
            # Get the message value
            transaction = message.value
            transaction_batch.append(transaction)
            
            # Process in batches
            if len(transaction_batch) >= batch_size:
                inserted = insert_transactions(conn, transaction_batch)
                count += inserted
                transaction_batch = []
                
                # Print progress
                current_time = time.time()
                elapsed = current_time - batch_start_time
                rate = batch_size / elapsed if elapsed > 0 else 0
                
                print(f"Inserted {count} processed transactions to PostgreSQL. "
                      f"Latest batch rate: {rate:.2f} transactions/second")
                
                # Reset timer for next batch
                batch_start_time = time.time()
    
    except KeyboardInterrupt:
        print("Stopping Processed Data to PostgreSQL connector...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Insert any remaining transactions
        if transaction_batch:
            try:
                inserted = insert_transactions(conn, transaction_batch)
                count += inserted
                print(f"Final batch: Inserted {inserted} transactions")
            except Exception as e:
                print(f"Error inserting final batch: {e}")
        
        # Close connections
        consumer.close()
        conn.close()
        print(f"Total inserted: {count} transactions")
        print("Connections closed.")

if __name__ == "__main__":
    main()
