import argparse  # Library to help read commands typed in terminal
import sys       # Library to interact with the system (like exiting)
from aws_lib.core import SessionManager
from aws_lib.stacks import StackManager
from aws_lib.audit import CostAuditor
from aws_lib.audit import CostAuditor
from aws_lib.easy_iam import EasyIAMManager
from aws_lib.easy_iam import EasyIAMManager
from aws_lib.pipeline import PipelineManager
from aws_lib.ai import DataAgent

# --- CONSTANTS ---
# These are names we use everywhere. Storing them here prevents typos later.
STACK_NETWORK = 'network-stack'    # Name for our VPC stack
STACK_WEBSITE = 'website-stack'    # Name for our Website stack
STACK_IAM = 'iam-stack'            # Name for our Admin User stack
STACK_EASY_IAM = 'easy-iam-stack'  # Name for the Generated stack
STACK_SES = 'ses-stack'            # Name for our Email Service
BUCKET_NAME = 'egirgis-lab'        # The specific name valid for your bucket

def handle_infrastructure(args, session):
    """
    This function handles all 'construction' work:
    - Building the Network (VPC)
    - Building the Website (S3)
    - Uploading the website files
    - Destroying everything
    """
    # 1. Initialize the Builder (StackManager)
    # We give it the 'session' (security badge) so it can talk to AWS.
    manager = StackManager(session)
    
    target = args.stack

    if args.action == 'deploy':
        print(f"--- Deploying Infrastructure ---")
        
        # Step A1: Deploy SES (Email Capability)
        if not target or target == 'ses':
             manager.deploy(STACK_SES, 'infrastructure/ses.yaml')

        # Step A2: Deploy the IAM Users (Foundation)
        if not target or target == 'iam':
            manager.deploy(STACK_IAM, 'infrastructure/iam.yaml')

        # Step B: Deploy the Network (VPC)
        # We tell the manager: "Make a stack named 'network-stack' using the file 'network.yaml'"
        if not target or target == 'network':
            manager.deploy(STACK_NETWORK, 'infrastructure/network.yaml')
        
        # Step C: Deploy the Website (S3)
        # We pass the 'BucketName' as a parameter because the YAML file asks for it.
        if not target or target == 'website':
            manager.deploy(STACK_WEBSITE, 'infrastructure/website.yaml', 
                        parameters={'BucketName': BUCKET_NAME})
        
        # Step C: Upload Content
        # Now that the bucket exists, we put the 'index.html' file inside it.
        if not target or target == 'website':
            manager.upload_file(BUCKET_NAME, 'website/index.html', 'index.html', 'text/html')
        
        # Final Step: Tell the user where to look
        # We ask AWS: "What is the WebsiteURL for this stack?"
        if not target or target == 'website':
            url = manager.get_output(STACK_WEBSITE, 'WebsiteURL')
            print(f"\nSUCCESS: Website is live at: {url}")

    elif args.action == 'destroy':
        print(f"--- Destroying Infrastructure ---")
        
        # Step A: Empty the Bucket
        # AWS forbids deleting a bucket if it has files in it. We must empty it first.
        manager.empty_bucket(BUCKET_NAME)
        
        # Step B: Delete the Stacks
        # We tear them down in reverse order (Website first, then Network, then IAM).
        if not target or target == 'website':
            manager.destroy(STACK_WEBSITE)
        if not target or target == 'network':
            manager.destroy(STACK_NETWORK)
        if not target or target == 'easy-iam':
            manager.destroy(STACK_EASY_IAM)
        if not target or target == 'iam':
            manager.destroy(STACK_IAM)
        if not target or target == 'ses':
            manager.destroy(STACK_SES)

    elif args.action == 'upload':
        # Just update the file, don't rebuild the infrastructure
        print(f"--- Uploading Content ---")
        manager.upload_file(BUCKET_NAME, 'website/index.html', 'index.html', 'text/html')
        print("Done.")

def handle_audit(args, session):
    """
    This function handles checking up on the account.
    """
    # Initialize the Auditor (CostAuditor)
    auditor = CostAuditor(session)
    
    if args.target == 'resources':
        # Check for running servers or unattached volumes
        auditor.audit_resources()
    elif args.target == 'cost':
        # Check how much money we spent this month
        auditor.get_monthly_cost()

def handle_manager(args, session):
    """
    Handles the "Easy Mode" IAM Manager.
    1. Reads Simple Spec
    2. Generates CloudFormation
    3. Deploys Stack
    4. Onboards Users (Passwords + Email)
    """
    manager = EasyIAMManager(session, args.spec_file)
    stack_manager = StackManager(session)

    if args.action == 'apply':
        # 1. Generate
        generated_file = 'infrastructure/iam_generated.yaml'
        manager.generate_cloudformation(generated_file)
        
        # 2. Deploy
        print(f"--- Deploying Generated IAM Stack ---")
        stack_manager.deploy(STACK_EASY_IAM, generated_file)
        
        # 3. Onboard
        manager.onboard_users()

def main():
    """
    Main Entry Point.
    This runs when you type 'python cli.py'
    """
    # 1. Setup the Argument Parser
    # We use a 'parent' parser to define arguments that are common to all commands (like --profile)
    # This check allows you to type '--profile' EITHER before OR after the command.
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--profile', help='AWS Profile to use', default=None)

    parser = argparse.ArgumentParser(description="AWS Playground CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # -- Command: infrastructure --
    # Allows: python cli.py infrastructure deploy --profile study
    infra_parser = subparsers.add_parser('infrastructure', 
                                         help='Manage CloudFormation Stacks',
                                         parents=[parent_parser])
    infra_parser.add_argument('action', choices=['deploy', 'destroy', 'upload'], help='Action to perform')
    infra_parser.add_argument('--stack', choices=['network', 'website', 'iam', 'ses', 'easy-iam'], help='Target specific stack')

    # -- Command: audit --
    # Allows: python cli.py audit cost --profile study
    audit_parser = subparsers.add_parser('audit', 
                                         help='Audit costs and resources',
                                         parents=[parent_parser])
    audit_parser.add_argument('target', choices=['resources', 'cost'], help='What to audit')

    # -- Command: manager (NEW) --
    # Allows: python cli.py manager apply my_team.simple.yaml
    manager_parser = subparsers.add_parser('manager',
                                           help='Easy Mode Identity Manager',
                                           parents=[parent_parser])
    manager_parser.add_argument('action', choices=['apply'], help='Action to perform')
    manager_parser.add_argument('spec_file', help='Path to your Simple Spec YAML file')

    # -- Command: pipeline (NEW) --
    # Allows: python cli.py pipeline deploy --profile study
    pipeline_parser = subparsers.add_parser('pipeline',
                                            help='Manage Cloud Data Pipeline',
                                            parents=[parent_parser])
    pipeline_parser.add_argument('action', choices=['deploy', 'upload-ingest', 'upload-job', 'create-job', 'start-job', 'create-crawler', 'start-crawler'], help='Action to perform')

    # -- Command: agent (NEW) --
    # Allows: python cli.py agent ask "How much revenue?" --profile study
    agent_parser = subparsers.add_parser('agent',
                                            help='Ask the AI Data Analyst',
                                            parents=[parent_parser])
    agent_parser.add_argument('action', choices=['ask'], help='Action to perform')
    agent_parser.add_argument('question', help='The question you want to ask the data')

    # 2. Read the arguments user typed
    args = parser.parse_args()

    # If user didn't type a command, show help and exit
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 3. Log in to AWS (Authentication)
    # We call our SessionManager to get the 'session' (Security Badge)
    session = SessionManager.get_session(args.profile)
    print(f"Using Profile: {session.profile_name}")

    # 4. Route to the right function
    if args.command == 'infrastructure':
        handle_infrastructure(args, session)
    elif args.command == 'audit':
        handle_audit(args, session)
    elif args.command == 'manager':
        handle_manager(args, session)
    elif args.command == 'pipeline':
        handle_pipeline(args, session)
    elif args.command == 'agent':
        handle_agent(args, session)

def handle_agent(args, session):
    """
    Handles AI interactions.
    """
    agent = DataAgent(session)
    DB_NAME = 'edu_etl_db'
    # Athena needs a bucket to store query results
    RESULTS_LOCATION = 's3://egirgis-datalake-v1/athena-results/'
    
    if args.action == 'ask':
        # 1. Get Context
        schema = agent.get_table_schema(DB_NAME)
        if not schema:
            print("Could not fetch schema. Did the crawler run?")
            return

        # 2. Get SQL from AI
        sql = agent.generate_sql(args.question, schema)
        if not sql: return
        
        # 3. Run SQL
        results = agent.run_query(sql, RESULTS_LOCATION)
        
        # 4. Show Answer
        agent.print_results(results)

def handle_pipeline(args, session):
    """
    Handles Data Pipeline tasks.
    """
    manager = PipelineManager(session)
    # Define a dedicated bucket for the datalake
    # We use a distinct name to avoid conflicts with the website bucket
    DATALAKE_BUCKET = 'egirgis-datalake-v1' 

    if args.action == 'deploy':
        manager.deploy_infra(DATALAKE_BUCKET)
    
    elif args.action == 'upload-ingest':
        # Uploads the ingestion script (mock)
        print("Uploading ingestion script...") 
        # Future: calls manager.upload_script(...)

    elif args.action == 'upload-job':
        script_path = 'cloud_intelligence_pipeline/glue_jobs/process_job.py'
        manager.upload_script(DATALAKE_BUCKET, script_path, 'scripts/process_job.py')

    elif args.action == 'create-job':
        # Create the Glue Job
        JOB_NAME = 'etl-process-orders'
        ROLE_NAME = 'GlueServiceRole-Playground'
        SCRIPT_S3 = f"{DATALAKE_BUCKET}/scripts/process_job.py"
        manager.create_glue_job(JOB_NAME, ROLE_NAME, SCRIPT_S3)

    elif args.action == 'start-job':
        JOB_NAME = 'etl-process-orders'
        manager.start_glue_job(JOB_NAME)

    elif args.action == 'create-crawler':
        CRAWLER_NAME = 'crawl-orders'
        ROLE_NAME = 'GlueServiceRole-Playground'
        DB_NAME = 'edu_etl_db'
        # Point to the folder containing data (IMPORTANT: must end with / for proper crawling usually, or just the path)
        TARGET_S3 = f"s3://{DATALAKE_BUCKET}/processed/orders_parquet/"
        manager.create_crawler(CRAWLER_NAME, ROLE_NAME, DB_NAME, TARGET_S3)

    elif args.action == 'start-crawler':
        CRAWLER_NAME = 'crawl-orders'
        manager.start_crawler(CRAWLER_NAME)


if __name__ == "__main__":
    main()
