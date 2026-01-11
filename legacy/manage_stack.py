import boto3
import sys
import os
import time
from botocore.exceptions import ClientError

STACK_NETWORK = 'network-stack'
STACK_WEBSITE = 'website-stack'

def get_session():
    profile = os.environ.get('AWS_PROFILE', 'study')
    return boto3.Session(profile_name=profile)

def stack_exists(client, stack_name):
    try:
        data = client.describe_stacks(StackName=stack_name)
        return data['Stacks'][0]['StackStatus']
    except ClientError:
        return None

def wait_for_stack(client, stack_name, operation):
    print(f"Waiting for {stack_name} to {operation}...")
    waiter = client.get_waiter(f'stack_{operation}_complete')
    waiter.wait(StackName=stack_name)
    print(f"{stack_name} {operation} complete.")

def deploy_stack(session, stack_name, template_file, parameters=None):
    client = session.client('cloudformation')
    
    with open(template_file, 'r') as f:
        template_body = f.read()

    params = []
    if parameters:
        for k, v in parameters.items():
            params.append({'ParameterKey': k, 'ParameterValue': v})

    status = stack_exists(client, stack_name)
    
    if status is None or status == 'REVIEW_IN_PROGRESS':
        print(f"Creating stack: {stack_name}")
        client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=params,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        wait_for_stack(client, stack_name, 'create')
    else:
        print(f"Updating stack: {stack_name}")
        try:
            client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=params,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            wait_for_stack(client, stack_name, 'update')
        except ClientError as e:
            if "No updates are to be performed" in str(e):
                print(f"No changes for {stack_name}.")
            else:
                raise e

def destroy_stack(session, stack_name):
    client = session.client('cloudformation')
    status = stack_exists(client, stack_name)
    if status:
        print(f"Deleting stack: {stack_name}")
        client.delete_stack(StackName=stack_name)
        wait_for_stack(client, stack_name, 'delete')
    else:
        print(f"Stack {stack_name} does not exist.")

def empty_bucket(session, bucket_name):
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        print(f"Emptying bucket {bucket_name}...")
        bucket.objects.all().delete()
        bucket.object_versions.all().delete()
    except ClientError as e:
        if "NoSuchBucket" not in str(e):
            print(f"Error emptying bucket: {e}")

def get_stack_output(session, stack_name, output_key):
    client = session.client('cloudformation')
    try:
        response = client.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0].get('Outputs', [])
        for o in outputs:
            if o['OutputKey'] == output_key:
                return o['OutputValue']
    except Exception:
        pass
    return None

def upload_website(session):
    bucket_name = get_stack_output(session, STACK_WEBSITE, 'BucketName')
    if not bucket_name:
        print("Could not find BucketName output from website stack.")
        return

    s3 = session.client('s3')
    print(f"Uploading index.html to {bucket_name}...")
    s3.upload_file('index.html', bucket_name, 'index.html', ExtraArgs={'ContentType': 'text/html'})
    
    url = get_stack_output(session, STACK_WEBSITE, 'WebsiteURL')
    print(f"Website deployed! URL: {url}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_stack.py [deploy|destroy]")
        sys.exit(1)

    action = sys.argv[1]
    session = get_session()
    print(f"Action: {action} | Profile: {session.profile_name}")

    if action == 'deploy':
        # 1. Deploy Network
        deploy_stack(session, STACK_NETWORK, 'infrastructure/network.yaml')
        
        # 2. Deploy Website
        # Using a fixed, meaningful name as requested
        deploy_stack(session, STACK_WEBSITE, 'infrastructure/website.yaml', 
                     parameters={'BucketName': 'egirgis-lab'})
        
        # 3. Upload Content
        upload_website(session)

    elif action == 'upload':
        upload_website(session)

    elif action == 'destroy':
        # 1. Empty Bucket First (CloudFormation cannot delete non-empty buckets)
        bucket_name = get_stack_output(session, STACK_WEBSITE, 'BucketName')
        if bucket_name:
            empty_bucket(session, bucket_name)
        
        # 2. Delete Stacks (Reverse order)
        destroy_stack(session, STACK_WEBSITE)
        destroy_stack(session, STACK_NETWORK)

if __name__ == "__main__":
    main()
