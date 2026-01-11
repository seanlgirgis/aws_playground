import boto3
import os
import sys
from botocore.exceptions import ProfileNotFound, ClientError

def get_session():
    """Defaults to 'study' profile unless AWS_PROFILE env var is set."""
    profile = os.environ.get('AWS_PROFILE', 'study')
    try:
        return boto3.Session(profile_name=profile)
    except ProfileNotFound:
        print(f"Error: Profile '{profile}' not found. Please run 'aws configure --profile {profile}'")
        sys.exit(1)

def audit_ec2(session):
    ec2 = session.resource('ec2')
    print("\n--- Checking EC2 Instances ---")
    instances = list(ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]))
    
    if not instances:
        print("OK: No running EC2 instances found.")
    else:
        for i in instances:
            print(f"WARNING: Instance {i.id} is RUNNING ({i.instance_type}) - Check if needed.")

def audit_volumes(session):
    ec2 = session.resource('ec2')
    print("\n--- Checking EBS Volumes ---")
    # "available" means not attached to any instance, but still costing money
    volumes = list(ec2.volumes.filter(Filters=[{'Name': 'status', 'Values': ['available']}]))
    
    if not volumes:
        print("OK: No unattached EBS volumes found.")
    else:
        for v in volumes:
            print(f"WARNING: Volume {v.id} is AVAILABLE ({v.size} GB) - unused but billable.")

def audit_nat_gateways(session):
    client = session.client('ec2')
    print("\n--- Checking NAT Gateways ---")
    try:
        response = client.describe_nat_gateways(Filters=[{'Name': 'state', 'Values': ['available']}])
        nats = response['NatGateways']
        if not nats:
            print("OK: No active NAT Gateways found.")
        else:
            for nat in nats:
                print(f"WARNING: NAT Gateway {nat['NatGatewayId']} is AVAILABLE - This is expensive!")
    except ClientError as e:
        print(f"Error checking NAT Gateways: {e}")

def main():
    print(f"Auditing Billable Resources for Profile: {os.environ.get('AWS_PROFILE', 'study')}")
    session = get_session()
    
    audit_ec2(session)
    audit_volumes(session)
    audit_nat_gateways(session)
    
    print("\nAudit Complete.")

if __name__ == "__main__":
    main()
