import boto3
import os
import sys
from datetime import datetime, timedelta
from botocore.exceptions import ProfileNotFound, ClientError

def get_session():
    profile = os.environ.get('AWS_PROFILE', 'study')
    try:
        return boto3.Session(profile_name=profile)
    except ProfileNotFound:
        print(f"Error: Profile '{profile}' not found.")
        sys.exit(1)

def get_cost_report():
    session = get_session()
    ce = session.client('ce')

    # Date range: First of this month to today
    now = datetime.utcnow()
    start_date = now.replace(day=1).strftime('%Y-%m-%d')
    end_date = now.strftime('%Y-%m-%d')

    if start_date == end_date:
        # If it's the 1st of the month, Cost Explorer might error if Start=End. 
        # Move start back one day or just warn.
        print("It's the first day of the month. Cost data might not be available yet.")
        return

    print(f"\n--- AWS Cost Report ({start_date} to {end_date}) ---")
    print(f"Profile: {session.profile_name}")

    try:
        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        results = response['ResultsByTime'][0]['Groups']
        total_cost = 0.0

        if not results:
            print("No cost data found for this period.")
            return

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
            print("\nError: Access Denied to Cost Explorer.")
            print("Note: The IAM user for profile 'study' needs the 'ce:GetCostAndUsage' permission.")
        else:
            print(f"Error fetching costs: {e}")

if __name__ == "__main__":
    get_cost_report()
