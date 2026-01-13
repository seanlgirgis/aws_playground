"""
Pipeline Infrastructure Manager
Handles provisioning of S3 Buckets, Glue Databases, and uploading scripts.
"""
import boto3
import os

class PipelineManager:
    def __init__(self, session):
        self.session = session
        self.s3 = session.client('s3')
        self.iam = session.client('iam')
        self.glue = session.client('glue')
        self.region = session.region_name

    def deploy_infra(self, bucket_name):
        """
        Creates S3 Bucket and required folders.
        """
        print(f"--- Deploying Pipeline Infrastructure to {self.region} ---")
        
        # 1. Create S3 Bucket
        try:
            self.s3.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket {bucket_name} already exists.")
        except Exception:
            print(f"Creating bucket {bucket_name}...")
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': self.region})
            print(f"✅ Bucket {bucket_name} created.")

        # 2. Create 'Folders' (Empty objects ending in /)
        folders = ['raw/', 'processed/', 'scripts/', 'athena-results/']
        for folder in folders:
            try:
                self.s3.put_object(Bucket=bucket_name, Key=folder)
                print(f"   - Folder created: {folder}")
            except Exception as e:
                print(f"   - Skipped folder {folder}: {e}")

        print("\n✅ Infrastructure Ready.")
        print(f"   Target Bucket: s3://{bucket_name}/")

    def upload_script(self, bucket_name, local_path, s3_key):
        """
        Uploads a local script to S3.
        """
        print(f"Uploading {local_path} -> s3://{bucket_name}/{s3_key}")
        try:
            self.s3.upload_file(local_path, bucket_name, s3_key)
            print("✅ Upload complete.")
        except Exception as e:
            print(f"❌ Upload failed: {e}")

    def create_glue_job(self, job_name, role_name, script_s3_path):
        """
        Creates (or updates) an AWS Glue Job.
        """
        print(f"--- Creating Glue Job: {job_name} ---")
        
        # 1. Get/Create IAM Role
        try:
            role_arn = self.iam.get_role(RoleName=role_name)['Role']['Arn']
            print(f"✅ Using existing Role: {role_arn}")
        except Exception:
            print(f"Creating Role {role_name}...")
            assume_role_policy = '{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Principal": {"Service": "glue.amazonaws.com"},"Action": "sts:AssumeRole"}]}'
            role = self.iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy)
            self.iam.attach_role_policy(RoleName=role_name, PolicyArn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole')
            # Add S3 Access (For playground simplicity, giving FullAccess, but scope down in production!)
            self.iam.attach_role_policy(RoleName=role_name, PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess')
            role_arn = role['Role']['Arn']
            print(f"✅ Role created: {role_arn}")
            # Wait for propagation
            import time
            time.sleep(10)

        # 2. Create Job
        job_args = {
            'Name': job_name,
            'Role': role_arn,
            'Command': {
                'Name': 'glueetl',
                'ScriptLocation': f"s3://{script_s3_path}",
                'PythonVersion': '3'
            },
            'DefaultArguments': {
                '--job-language': 'python'
            },
            'GlueVersion': '3.0',
            'WorkerType': 'G.1X',
            'NumberOfWorkers': 2
        }
        
        try:
            self.glue.create_job(**job_args)
            print(f"✅ Job {job_name} created successfully.")
        except self.glue.exceptions.IdempotentParameterMismatchException:
            print(f"⚠️ Job {job_name} exists with different parameters. Updating...")
            self.glue.update_job(JobName=job_name, JobUpdate=job_args)
            print(f"✅ Job {job_name} updated.")
        except self.glue.exceptions.AlreadyExistsException:
             print(f"✅ Job {job_name} already exists.")
        except Exception as e:
            print(f"❌ Failed to create job: {e}")

    def start_glue_job(self, job_name):
        """
        Triggers a Glue Job run.
        """
        print(f"--- Starting Glue Job: {job_name} ---")
        try:
            response = self.glue.start_job_run(JobName=job_name)
            run_id = response['JobRunId']
            print(f"✅ Job started! Run ID: {run_id}")
            print(f"   Monitor at: https://{self.region}.console.aws.amazon.com/glue/home?region={self.region}#jobRun:jobName={job_name};jobRunId={run_id}")
        except Exception as e:
            print(f"❌ Failed to start job: {e}")

    def create_crawler(self, crawler_name, role_name, db_name, s3_target):
        """
        Creates a Glue Crawler to catalog the data.
        """
        print(f"--- Creating Glue Crawler: {crawler_name} ---")
        
        # 1. Ensure Database Exists
        try:
            self.glue.create_database(DatabaseInput={'Name': db_name})
            print(f"✅ Database {db_name} created (or verified).")
        except self.glue.exceptions.AlreadyExistsException:
             print(f"✅ Database {db_name} already exists.")

        # 2. Create Crawler
        # We point it to the 'processed' folder where Parquet files live
        targets = {'S3Targets': [{'Path': s3_target}]}
        try:
            self.glue.create_crawler(
                Name=crawler_name,
                Role=role_name,
                DatabaseName=db_name,
                Targets=targets,
                TablePrefix='clean_'
            )
            print(f"✅ Crawler {crawler_name} created.")
        except self.glue.exceptions.AlreadyExistsException:
            print(f"✅ Crawler {crawler_name} exists. Updating...")
            self.glue.update_crawler(Name=crawler_name, Role=role_name, DatabaseName=db_name, Targets=targets)

    def start_crawler(self, crawler_name):
        print(f"--- Starting Crawler: {crawler_name} ---")
        try:
            self.glue.start_crawler(Name=crawler_name)
            print("✅ Crawler started! It will inspect S3 and create tables.")
        except Exception as e:
             print(f"❌ Failed to start crawler: {e}")
