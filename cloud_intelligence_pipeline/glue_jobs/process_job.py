"""
AWS Glue Job: Process Orders
Reads raw JSON from S3 -> Transformations -> Writes Parquet to S3.
"""
import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, sum, avg, max

# Initialize Glue Context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init("ProcessOrders", {})

# CONFIG
BUCKET_NAME = "egirgis-datalake-v1"
INPUT_PATH = f"s3://{BUCKET_NAME}/raw/orders.json"
OUTPUT_PATH = f"s3://{BUCKET_NAME}/processed/orders_parquet"

print(f"Reading from {INPUT_PATH}...")
df = spark.read.option("multiLine", True).json(INPUT_PATH)

# Feature Engineering

# Feature Engineering
df = df.withColumn("revenue", col("price") * col("quantity"))

# Aggregation (Business Logic)
results = df.groupBy("category").agg(
    sum("revenue").alias("total_revenue"),
    avg("price").alias("avg_price"),
    max("quantity").alias("max_quantity")
)

# Write to S3 (Parquet) - Overwrite mode
print(f"Writing to {OUTPUT_PATH}...")
results.write.mode("overwrite").parquet(OUTPUT_PATH)

job.commit()
