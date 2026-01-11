# The Inspector: `aws_lib/audit.py`

## Role
This file is the **Auditor**. It doesn't build anything; it checks on what exists.

## What it does
It uses the "Read-Only" parts of AWS to find running servers and calculate costs. This is useful for saving money and ensuring you didn't leave anything running by mistake.

## Key Class: `CostAuditor`

### Main Functions
1.  **`audit_resources()`**
    *   Runs a safety check.
    *   **Checks EC2**: Warns if any virtual computer is in the `running` state.
    *   **Checks EBS**: Warns if any hard drive is `available` (unattached but costing money).
    *   **Checks NAT Gateways**: Warns if these expensive networking devices are active.

2.  **`get_monthly_cost()`**
    *   Queries **AWS Cost Explorer**.
    *   Asks for a report from the 1st of the month until today.
    *   Groups the cost by Service (e.g., how much for EC2? how much for S3?).
    *   Prints a neat table of your spending.
