#!/usr/bin/env python3
"""
Banking Transaction MongoDB Reader
This script reads and displays the banking transaction data stored in MongoDB.
"""

import pymongo
from pymongo import MongoClient
import time
from datetime import datetime
import json

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'banking'
COLLECTION_NAME = 'transactions'

def connect_to_mongodb():
    """Connect to MongoDB and return the collection."""
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return db[COLLECTION_NAME]

def display_transaction_summary(collection):
    """Display a summary of transactions including fraud statistics."""
    total_count = collection.count_documents({})
    fraud_count = collection.count_documents({"fraud_bool": 1})
    legitimate_count = collection.count_documents({"fraud_bool": 0})
    
    fraud_percentage = (fraud_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n{'='*80}")
    print(f"Banking Transaction Summary as of {datetime.now()}")
    print(f"{'='*80}")
    print(f"Total transactions: {total_count}")
    print(f"Fraudulent transactions: {fraud_count} ({fraud_percentage:.2f}%)")
    print(f"Legitimate transactions: {legitimate_count} ({100-fraud_percentage:.2f}%)")
    
    # Find the latest transaction
    latest = collection.find_one(sort=[("stream_timestamp", pymongo.DESCENDING)])
    if latest:
        print(f"\nLatest transaction timestamp: {latest.get('stream_timestamp')}")

def display_transactions(collection, limit=5):
    """Display the most recent banking transactions from MongoDB collection."""
    print(f"\n{'='*80}")
    print(f"Latest Banking Transactions in {DATABASE_NAME}.{COLLECTION_NAME}")
    print(f"{'='*80}")
    
    count = collection.count_documents({})
    if count == 0:
        print("No transactions found in the collection.")
        return
    
    # Display most recent transactions
    print(f"Showing {min(limit, count)} of {count} total transactions:")
    for doc in collection.find().sort('stream_timestamp', pymongo.DESCENDING).limit(limit):
        is_fraud = "YES" if doc.get('fraud_bool') == 1 else "NO"
        print(f"Fraud: {is_fraud}")
        print(f"Credit Risk Score: {doc.get('credit_risk_score')}")
        print(f"Customer Age: {doc.get('customer_age')}")
        print(f"Income: ${doc.get('income', 0):.2f}")
        print(f"Intended Amount: ${doc.get('intended_balcon_amount', 0):.2f}")
        print(f"Employment: {doc.get('employment_status')}")
        print(f"Housing: {doc.get('housing_status')}")
        print(f"Payment Type: {doc.get('payment_type')}")
        print(f"Stream Timestamp: {doc.get('stream_timestamp')}")
        print(f"Processing Timestamp: {doc.get('mongodb_insertion_timestamp')}")
        print('-' * 50)

def main():
    """Main function to periodically read from MongoDB."""
    print("Connecting to MongoDB...")
    collection = connect_to_mongodb()
    
    try:
        while True:
            display_transaction_summary(collection)
            display_transactions(collection)
            print("\nChecking again in 10 seconds...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
