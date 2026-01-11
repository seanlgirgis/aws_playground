import botocore
from botocore.exceptions import ClientError
import time
import os

class StackManager:
    """
    The 'Builder' class.
    It talks to AWS CloudFormation to create, update, or delete lists of resources (Stacks).
    It also helps with S3 bucket tasks (uploading files).
    """

    def __init__(self, session):
        """
        Setup the tool. We need the 'session' (Security Badge) to prove who we are.
        """
        self.session = session
        # Client for telling AWS "Build this stack"
        self.cfn = session.client('cloudformation')
        # Resource for "Put this file in that bucket"
        self.s3 = session.resource('s3')
        # Client for lower-level S3 commands
        self.s3_client = session.client('s3')

    def stack_exists(self, stack_name):
        """
        Checks if a stack with this name already exists in AWS.
        Returns the status (like 'CREATE_COMPLETE') if yes, or None if no.
        """
        try:
            data = self.cfn.describe_stacks(StackName=stack_name)
            return data['Stacks'][0]['StackStatus']
        except ClientError:
            # If AWS says "I can't find that stack", we catch the error and return None
            return None

    def _wait_for_completion(self, stack_name, operation):
        """
        Private Helper Function (starts with _).
        AWS takes time to build things (minutes). This function pauses our script
        until AWS says "I'm done!".
        
        Args:
            operation: 'create', 'update', or 'delete'
        """
        print(f"Waiting for {stack_name} to {operation}...")
        
        # A 'waiter' is a tool provided by boto3 that polls AWS every few seconds
        waiter = self.cfn.get_waiter(f'stack_{operation}_complete')
        
        try:
            waiter.wait(StackName=stack_name)
            print(f"{stack_name} {operation} complete.")
        except Exception as e:
            print(f"Error waiting for stack {operation}: {e}")

    def deploy(self, stack_name, template_path, parameters=None):
        """
        The Main Build Function.
        1. Reads your YAML blueprint.
        2. Checks if the stack exists.
        3. Creates it (if new) or Updates it (if existing).
        """
        # A. Read the Blueprint file
        if not os.path.exists(template_path):
            print(f"Error: Template {template_path} not found.")
            return

        with open(template_path, 'r') as f:
            template_body = f.read()

        # B. Format the Parameters (Questions/Answers for the template)
        params = []
        if parameters:
            for k, v in parameters.items():
                params.append({'ParameterKey': k, 'ParameterValue': v})

        # C. Check if we are Creating or Updating
        status = self.stack_exists(stack_name)
        
        if status is None or status == 'REVIEW_IN_PROGRESS':
            # --- CREATE NEW ---
            print(f"Creating stack: {stack_name}")
            try:
                self.cfn.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=params,
                    Capabilities=['CAPABILITY_NAMED_IAM'] # Permission to name things (like Roles) explicitely
                )
                self._wait_for_completion(stack_name, 'create')
            except ClientError as e:
                print(f"Error creating stack: {e}")
        else:
            # --- UPDATE EXISTING ---
            print(f"Updating stack: {stack_name}")
            try:
                self.cfn.update_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=params,
                    Capabilities=['CAPABILITY_NAMED_IAM']
                )
                self._wait_for_completion(stack_name, 'update')
            except ClientError as e:
                # AWS throws an error if we say "Update" but changed nothing. We ignore that specific error.
                if "No updates are to be performed" in str(e):
                    print(f"No changes for {stack_name}.")
                else:
                    print(f"Error updating stack: {e}")

    def destroy(self, stack_name):
        """
        Tears down the stack.
        """
        status = self.stack_exists(stack_name)
        if status:
            print(f"Deleting stack: {stack_name}")
            self.cfn.delete_stack(StackName=stack_name)
            self._wait_for_completion(stack_name, 'delete')
        else:
            print(f"Stack {stack_name} does not exist.")

    def get_output(self, stack_name, output_key):
        """
        Reads the 'Outputs' section of a built stack.
        Useful for getting the WebsiteURL after it's built.
        """
        try:
            response = self.cfn.describe_stacks(StackName=stack_name)
            outputs = response['Stacks'][0].get('Outputs', [])
            for o in outputs:
                if o['OutputKey'] == output_key:
                    return o['OutputValue']
        except Exception:
            pass
        return None

    def empty_bucket(self, bucket_name):
        """
        Safety Helper.
        You cannot delete an S3 bucket if it has files. This deletes all files first.
        """
        bucket = self.s3.Bucket(bucket_name)
        try:
            print(f"Emptying bucket {bucket_name}...")
            # Delete all objects
            bucket.objects.all().delete()
            # Delete all versions (if versioning was enabled)
            bucket.object_versions.all().delete()
        except ClientError as e:
            if "NoSuchBucket" not in str(e):
                print(f"Error emptying bucket: {e}")

    def upload_file(self, bucket_name, local_path, s3_key, content_type=None):
        """
        Uploads a single file to S3.
        """
        try:
            print(f"Uploading {local_path} to {bucket_name}...")
            extra_args = {}
            if content_type:
                # We tell S3 what kind of file this is (e.g., 'text/html')
                # so the browser knows how to display it.
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_file(local_path, bucket_name, s3_key, ExtraArgs=extra_args)
        except Exception as e:
            print(f"Error uploading file: {e}")
