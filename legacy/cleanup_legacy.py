import boto3
import sys
import os

def get_session():
    profile = os.environ.get('AWS_PROFILE', 'study')
    try:
        return boto3.Session(profile_name=profile)
    except Exception as e:
        print(f"Error loading profile '{profile}': {e}")
        sys.exit(1)

def cleanup_s3(session):
    s3 = session.resource('s3')
    print("\n--- Cleaning up Legacy S3 Buckets ---")
    
    # List all buckets and filter by name pattern locally
    # (S3 API doesn't support server-side filtering by name/tag easily for list_buckets)
    try:
        for bucket in s3.buckets.all():
            if bucket.name.startswith("egirg-study-playground-"):
                print(f"Found bucket: {bucket.name}")
                confirmation = input(f"  > DELETE {bucket.name} and ALL contents? (y/n): ").lower()
                if confirmation == 'y':
                    try:
                        print("    Emptying bucket...")
                        bucket.objects.all().delete()
                        bucket.object_versions.all().delete()
                        print("    Deleting bucket...")
                        bucket.delete()
                        print("    Done.")
                    except Exception as e:
                        print(f"    ERROR: {e}")
                else:
                    print("    Skipped.")
    except Exception as e:
        print(f"Error listing buckets: {e}")

def cleanup_vpc(session):
    ec2 = session.resource('ec2')
    client = session.client('ec2')
    print("\n--- Cleaning up Legacy VPC ---")

    # Find VPC by Tag
    filters = [{'Name': 'tag:Name', 'Values': ['Playground-VPC']}]
    vpcs = list(ec2.vpcs.filter(Filters=filters))

    if not vpcs:
        print("No legacy VPC found with tag Name=Playground-VPC")
        return

    for vpc in vpcs:
        print(f"Found VPC: {vpc.id} ({vpc.tags})")
        confirmation = input(f"  > DELETE VPC {vpc.id}? This will delete all subnets/IGWs inside. (y/n): ").lower()
        if confirmation != 'y':
            print("    Skipped.")
            continue

        try:
            # 1. Delete Internet Gateways
            for igw in vpc.internet_gateways.all():
                print(f"    Detaching & Deleting IGW {igw.id}...")
                igw.detach_from_vpc(VpcId=vpc.id)
                igw.delete()

            # 2. Delete Subnets
            for subnet in vpc.subnets.all():
                print(f"    Deleting Subnet {subnet.id}...")
                subnet.delete()

            # 3. Delete Route Tables (Main RT cannot be deleted, custom ones can)
            for rt in vpc.route_tables.all():
                is_main = False
                for assoc in rt.associations:
                    if assoc.main:
                        is_main = True
                        break
                if not is_main:
                    print(f"    Deleting Route Table {rt.id}...")
                    try:
                        rt.delete()
                    except Exception as e_rt:
                        print(f"    Error deleting RT {rt.id}: {e_rt}")

            # 4. Delete VPC
            print(f"    Deleting VPC {vpc.id}...")
            vpc.delete()
            print("    Done.")

        except Exception as e:
            print(f"    ERROR cleaning VPC: {e}")

if __name__ == "__main__":
    session = get_session()
    print(f"Using Profile: {session.profile_name}")
    
    cleanup_s3(session)
    cleanup_vpc(session)
    print("\nLegacy Cleanup Finished.")
