import argparse  # Library to help read commands typed in terminal
import sys       # Library to interact with the system (like exiting)
from aws_lib.core import SessionManager
from aws_lib.stacks import StackManager
from aws_lib.audit import CostAuditor

# --- CONSTANTS ---
# These are names we use everywhere. Storing them here prevents typos later.
STACK_NETWORK = 'network-stack'    # Name for our VPC stack
STACK_WEBSITE = 'website-stack'    # Name for our Website stack
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
    
    if args.action == 'deploy':
        print(f"--- Deploying Infrastructure ---")
        
        # Step A: Deploy the Network (VPC)
        # We tell the manager: "Make a stack named 'network-stack' using the file 'network.yaml'"
        manager.deploy(STACK_NETWORK, 'infrastructure/network.yaml')
        
        # Step B: Deploy the Website (S3)
        # We pass the 'BucketName' as a parameter because the YAML file asks for it.
        manager.deploy(STACK_WEBSITE, 'infrastructure/website.yaml', 
                       parameters={'BucketName': BUCKET_NAME})
        
        # Step C: Upload Content
        # Now that the bucket exists, we put the 'index.html' file inside it.
        manager.upload_file(BUCKET_NAME, 'website/index.html', 'index.html', 'text/html')
        
        # Final Step: Tell the user where to look
        # We ask AWS: "What is the WebsiteURL for this stack?"
        url = manager.get_output(STACK_WEBSITE, 'WebsiteURL')
        print(f"\nSUCCESS: Website is live at: {url}")

    elif args.action == 'destroy':
        print(f"--- Destroying Infrastructure ---")
        
        # Step A: Empty the Bucket
        # AWS forbids deleting a bucket if it has files in it. We must empty it first.
        manager.empty_bucket(BUCKET_NAME)
        
        # Step B: Delete the Stacks
        # We tear them down in reverse order (Website first, then Network).
        manager.destroy(STACK_WEBSITE)
        manager.destroy(STACK_NETWORK)

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

def main():
    """
    Main Entry Point.
    This runs when you type 'python cli.py'
    """
    # 1. Setup the Argument Parser
    # This teaches the program what commands to expect (like 'infrastructure' or 'audit')
    parser = argparse.ArgumentParser(description="AWS Playground CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # -- Command: infrastructure --
    # Allows: python cli.py infrastructure deploy
    infra_parser = subparsers.add_parser('infrastructure', help='Manage CloudFormation Stacks')
    infra_parser.add_argument('action', choices=['deploy', 'destroy', 'upload'], help='Action to perform')

    # -- Command: audit --
    # Allows: python cli.py audit cost
    audit_parser = subparsers.add_parser('audit', help='Audit costs and resources')
    audit_parser.add_argument('target', choices=['resources', 'cost'], help='What to audit')

    # -- Global Arguments --
    # Allows specifying a different profile: python cli.py --profile my-other-profile ...
    parser.add_argument('--profile', help='AWS Profile to use', default=None)

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

if __name__ == "__main__":
    main()
