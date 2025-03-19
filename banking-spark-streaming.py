#!/usr/bin/env python3
"""
Banking Transaction Spark Streaming Processor
This script processes banking transaction data from Kafka using Spark Streaming.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, current_timestamp, lit, when
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType

def create_spark_session():
    """Create a Spark session with the necessary configurations."""
    return (SparkSession.builder
            .appName("BankingTransactionProcessor")
            .config("spark.jars.packages", 
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5")
            .getOrCreate())

def read_from_kafka(spark):
    """Read streaming data from Kafka topic."""
    return (spark
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", "banking-transactions")
            .option("startingOffsets", "latest")
            .load())

def define_schema():
    """Define the schema for the banking transaction data."""
    return StructType([
        StructField("fraud_bool", IntegerType(), True),
        StructField("income", DoubleType(), True),
        StructField("name_email_similarity", DoubleType(), True),
        StructField("prev_address_months_count", IntegerType(), True),
        StructField("current_address_months_count", IntegerType(), True),
        StructField("customer_age", IntegerType(), True),
        StructField("days_since_request", DoubleType(), True),
        StructField("intended_balcon_amount", DoubleType(), True),
        StructField("payment_type", StringType(), True),
        StructField("zip_count_4w", IntegerType(), True),
        StructField("velocity_6h", DoubleType(), True),
        StructField("velocity_24h", DoubleType(), True),
        StructField("velocity_4w", DoubleType(), True),
        StructField("bank_branch_count_8w", IntegerType(), True),
        StructField("date_of_birth_distinct_emails_4w", IntegerType(), True),
        StructField("employment_status", StringType(), True),
        StructField("credit_risk_score", IntegerType(), True),
        StructField("email_is_free", IntegerType(), True),
        StructField("housing_status", StringType(), True),
        StructField("phone_home_valid", IntegerType(), True),
        StructField("phone_mobile_valid", IntegerType(), True),
        StructField("bank_months_count", IntegerType(), True),
        StructField("has_other_cards", IntegerType(), True),
        StructField("proposed_credit_limit", DoubleType(), True),
        StructField("foreign_request", IntegerType(), True),
        StructField("source", StringType(), True),
        StructField("session_length_in_minutes", DoubleType(), True),
        StructField("device_os", StringType(), True),
        StructField("keep_alive_session", IntegerType(), True),
        StructField("device_distinct_emails_8w", IntegerType(), True),
        StructField("device_fraud_count", IntegerType(), True),
        StructField("month", IntegerType(), True),
        StructField("stream_timestamp", StringType(), True)
    ])

def process_data(df):
    """Process the incoming transaction data."""
    # Define schema for the JSON data
    schema = define_schema()
    
    # Parse JSON values and select relevant fields
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")
    
    # Add processing timestamp
    processed_df = parsed_df.withColumn("spark_processing_timestamp", current_timestamp())
    
    # Add risk category column based on credit_risk_score
    processed_df = processed_df.withColumn(
        "risk_category",
        when(col("credit_risk_score") >= 700, "LOW")
        .when(col("credit_risk_score") >= 500, "MEDIUM")
        .otherwise("HIGH")
    )
    
    # Add fraud probability column (this would be replaced by actual model predictions)
    processed_df = processed_df.withColumn(
        "fraud_probability", 
        when(col("fraud_bool") == 1, lit(0.8))
        .otherwise(lit(0.2))
    )
    
    return processed_df

def start_console_output(df):
    """Start streaming the processed data to console for debugging."""
    return (df.writeStream
              .outputMode("append")
              .format("console")
              .option("truncate", "false")
              .start())

def start_kafka_output(df, output_topic="processed-transactions"):
    """Stream the processed data back to a Kafka topic."""
    # Prepare the data for Kafka by converting to JSON
    kafka_output = df.select(
        to_json(struct("*")).alias("value")
    )
    
    # Write to Kafka
    return (kafka_output.writeStream
              .format("kafka")
              .option("kafka.bootstrap.servers", "localhost:9092")
              .option("topic", output_topic)
              .option("checkpointLocation", "/tmp/spark_checkpoint")
              .outputMode("append")
              .start())

def main():
    """Main function to set up and start the streaming pipeline."""
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Read from Kafka
    kafka_df = read_from_kafka(spark)
    
    # Process data
    processed_df = process_data(kafka_df)
    
    # Output to console for debugging
    console_query = start_console_output(processed_df)
    
    # Output to Kafka for further processing
    kafka_query = start_kafka_output(processed_df)
    
    # Wait for the streaming queries to terminate
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()
