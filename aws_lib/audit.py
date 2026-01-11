from datetime import datetime, timezone
import botocore
from botocore.exceptions import ClientError

class CostAuditor:
    """
    The 'Inspector' class.
    It doesn't build anything. It just looks at what we have and what we spent.
    """
    
    def __init__(self, session):
        self.session = session
        # We need different 'clients' for different services:
        self.ec2 = session.resource('ec2')      # For finding Computers (Instances)
        self.ec2_client = session.client('ec2') # For finding NAT Gateways
        self.rds = session.client('rds')        # For Databases
        self.lambda_client = session.client('lambda') # For Serverless Functions
        self.bedrock = session.client('bedrock') # For AI Models
        self.ce = session.client('ce')          # For Cost Explorer ($$$)

    def audit_resources(self):
        """
        Runs a check on expensive resources that might be left running.
        """
        print(f"\nAudit Report for Profile: {self.session.profile_name}")
        print(f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self._check_ec2()
        self._check_volumes()
        self._check_nat_gateways()
        self._check_rds()
        self._check_lambda()
        self._check_bedrock()

    def _check_ec2(self):
        print("\n--- Checking EC2 Instances ---")
        # filter() lets us find only the ones that match our criteria (State=running)
        instances = list(self.ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]))
        
        if not instances:
            print("OK: No running EC2 instances found.")
        else:
            for i in instances:
                print(f"WARNING: Instance {i.id} is RUNNING ({i.instance_type})")

    def _check_volumes(self):
        print("\n--- Checking EBS Volumes ---")
        # EBS Volumes are 'Hard Drives'. If they are 'available', it means they are
        # NOT attached to any computer, but you are still paying for them!
        volumes = list(self.ec2.volumes.filter(Filters=[{'Name': 'status', 'Values': ['available']}]))
        
        if not volumes:
            print("OK: No unattached EBS volumes found.")
        else:
            for v in volumes:
                print(f"WARNING: Volume {v.id} is AVAILABLE ({v.size} GB)")

    def _check_nat_gateways(self):
        print("\n--- Checking NAT Gateways ---")
        try:
            # NAT Gateways are expensive (~$30/month). We want to find any that are 'available' (active).
            response = self.ec2_client.describe_nat_gateways(Filters=[{'Name': 'state', 'Values': ['available']}])
            nats = response['NatGateways']
            if not nats:
                print("OK: No active NAT Gateways found.")
            else:
                for nat in nats:
                    print(f"WARNING: NAT Gateway {nat['NatGatewayId']} is AVAILABLE.")
        except ClientError as e:
            print(f"Error checking NAT Gateways: {e}")

    def _check_rds(self):
        print("\n--- Checking RDS Databases ---")
        try:
            # RDS Databases charge per hour if they are 'available' (running).
            response = self.rds.describe_db_instances()
            dbs = response['DBInstances']
            if not dbs:
                print("OK: No RDS instances found.")
            else:
                for db in dbs:
                    print(f"WARNING: DB Instance {db['DBInstanceIdentifier']} is {db['DBInstanceStatus']} ({db['DBInstanceClass']})")
        except ClientError as e:
            print(f"Error checking RDS: {e}")

    def _check_lambda(self):
        print("\n--- Checking Lambda Functions ---")
        try:
            # Lambdas usually cost only when run, but having many CAN imply hidden costs/triggers.
            # We list them so you know what's there.
            response = self.lambda_client.list_functions()
            funcs = response['Functions']
            if not funcs:
                print("OK: No Lambda functions found.")
            else:
                print(f"Found {len(funcs)} Lambda functions:")
                for f in funcs:
                    print(f" - {f['FunctionName']} ({f['Runtime']})")
        except ClientError as e:
            print(f"Error checking Lambda: {e}")

    def _check_bedrock(self):
        print("\n--- Checking Bedrock (AI) ---")
        try:
            # Bedrock charges for 'Provisioned Throughput' (reserved capacity).
            # On-Demand usage is not 'running' resource, so it won't show here unless we query logs.
            response = self.bedrock.list_provisioned_model_throughputs()
            models = response.get('provisionedModelSummaries', [])
            
            if not models:
                print("OK: No Provisioned Throughput (Recurring Cost) found.")
            else:
                for m in models:
                    print(f"WARNING: Provisioned Model {m['modelArn']} is Active!")
        except ClientError as e:
             # Bedrock might not be enabled in all regions or for all users
            if "AccessDeniedException" in str(e) or "UnrecognizedClientException" in str(e):
                 print("Note: Unable to check Bedrock (might not be enabled/available).")
            else:
                print(f"Error checking Bedrock: {e}")

    def get_monthly_cost(self):
        """
        Queries AWS Cost Explorer for the current month's bill.
        """
        # 1. Figure out the date range (Start of month -> Today)
        now = datetime.now(timezone.utc)
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')

        if start_date == end_date:
            print(f"Report Date: {start_date}")
            print("It's the first day of the month. Cost data might not be available yet.")
            return

        print(f"\n--- AWS Cost Report ({start_date} to {end_date}) ---")
        
        try:
            # 2. Ask AWS for the data
            response = self.ce.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'], # 'Unblended' is the standard cost metric
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}] # Group by 'EC2', 'S3', etc.
            )

            results = response['ResultsByTime'][0]['Groups']
            total_cost = 0.0

            if not results:
                print("No cost data found or $0.00 spend.")
                return

            # Print a nice table
            print(f"{'Service':<40} {'Cost ($)':>10}")
            print("-" * 52)

            for item in results:
                service_name = item['Keys'][0]
                amount = float(item['Metrics']['UnblendedCost']['Amount'])
                if amount > 0:
                    print(f"{service_name:<40} {amount:>10.2f}")
                    total_cost += amount
            
            print("-" * 52)
            print(f"{'TOTAL':<40} {total_cost:>10.2f}")

        except ClientError as e:
            if "AccessDeniedException" in str(e):
                print("Error: Access Denied to Cost Explorer. Your account might not have permissions enabled.")
            else:
                print(f"Error fetching costs: {e}")
