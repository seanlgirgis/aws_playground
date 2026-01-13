
import boto3
session = boto3.Session(profile_name='study')
glue = session.client('glue')

print("--- Job Status ---")
try:
    runs = glue.get_job_runs(JobName='etl-process-orders', MaxResults=1)
    status = runs['JobRuns'][0]['JobRunState']
    print(f"Job Status: {status}")
    if status == 'FAILED':
        print(f"Error: {runs['JobRuns'][0].get('ErrorMessage', 'Unknown Error')}")
except Exception as e:
    print(f"Error getting job: {e}")

except Exception as e:
    print(f"Error getting crawler: {e}")

print("\n--- S3 Status (Processed) ---")
try:
    s3 = session.client('s3')
    objects = s3.list_objects_v2(Bucket='egirgis-datalake-v1', Prefix='processed/orders_parquet/')
    if 'Contents' in objects:
        print(f"✅ Found {len(objects['Contents'])} files/folders in processed/")
        for obj in objects['Contents']:
            print(f"   - {obj['Key']} ({obj['Size']} bytes)")
    else:
        print("❌ S3 Processed folder is EMPTY. Job likely failed or didn't write.")
except Exception as e:
    print(f"Error checking S3: {e}")
