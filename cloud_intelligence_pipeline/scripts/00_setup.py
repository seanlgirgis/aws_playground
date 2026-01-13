"""
Pipeline Setup Script (00_setup.py)

This script is responsible for provisioning the Cloud Infrastructure for our Data Lake.
We will use CloudFormation (via boto3) to create:
1. S3 Bucket (Raw & Processed)
2. Glue Service Role (Security)
3. Glue Database (Catalog)

We will integrate this into the main 'cli.py' as a new command: 'pipeline'.
"""

import boto3
import time

def deploy_pipeline_infra(session, bucket_name):
    """
    Deploys the necessary AWS resources.
    For simplicity, we will use boto3 directly to check/create the bucket first.
    Later we can wrap this in CloudFormation.
    """
    s3 = session.client('s3')
    region = session.region_name
    
    print(f"--- Deploying Pipeline Infrastructure to {region} ---")
    
    # 1. Create S3 Bucket (if not exists)
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket {bucket_name} already exists.")
    except Exception:
        print(f"Creating bucket {bucket_name}...")
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
        print(f"✅ Bucket {bucket_name} created.")

    # 2. Upload the scripts folder to S3 (so Glue can find the PySpark script later)
    # We will assume a 'glue_jobs' folder exists locally
    # s3.upload_file('cloud_intelligence_pipeline/glue_jobs/process.py', bucket_name, 'scripts/process.py')
    
    print("\nNext Step: Run ingestion script to upload raw data.")
