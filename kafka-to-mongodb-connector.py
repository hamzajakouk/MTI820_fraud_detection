#!/usr/bin/env python3
"""
Kafka to MongoDB Connector
This script consumes banking transaction data from Kafka and stores it directly in MongoDB.
"""

import json
import time
from kafka import KafkaConsumer
import pymongo
from datetime import datetime

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC_NAME = 'banking-transactions'
CONSUMER_GROUP_ID = 'banking-mongodb-group'

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'banking'
COLLECTION_NAME = 'transactions'

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

def connect_to_mongodb():
    """Connect to MongoDB and return the client and collection."""
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    return client, collection

def process_message(message, collection):
    """Process a message from Kafka and store it in MongoDB."""
    try:
        # Add MongoDB insertion timestamp
        message.update({
            'mongodb_insertion_timestamp': datetime.now().isoformat()
        })
        
        # Insert into MongoDB
        result = collection.insert_one(message)
        return result.inserted_id
    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")
        return None

def main():
    """Main function to consume from Kafka and write to MongoDB."""
    print(f"Starting Kafka to MongoDB connector for topic {TOPIC_NAME}...")
    
    # Create consumer
    consumer = create_kafka_consumer()
    
    # Connect to MongoDB
    mongo_client, collection = connect_to_mongodb()
    
    # Process counter
    count = 0
    batch_start_time = time.time()
    
    try:
        for message in consumer:
            # Get the message value
            transaction = message.value
            
            # Process and store in MongoDB
            inserted_id = process_message(transaction, collection)
            
            if inserted_id:
                count += 1
                
                # Print progress every 10 messages
                if count % 10 == 0:
                    current_time = time.time()
                    elapsed = current_time - batch_start_time
                    rate = 10 / elapsed if elapsed > 0 else 0
                    
                    print(f"Processed {count} transactions. "
                          f"Latest batch rate: {rate:.2f} transactions/second")
                    
                    # Reset timer for next batch
                    batch_start_time = current_time
    
    except KeyboardInterrupt:
        print("Stopping Kafka to MongoDB connector...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Close connections
        consumer.close()
        mongo_client.close()
        print("Connections closed.")

if __name__ == "__main__":
    main()
