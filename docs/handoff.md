# AWS Playground Handoff Document

**Date:** 2026-04-27
**Status:** Operational / Verified

## 1. Project Overview
The `aws_playground` repository is a comprehensive learning and engineering environment designed to master AWS services across Infrastructure, Data Engineering, and AI/ML. It follows the "Infrastructure as Code" (IaC) philosophy, using CloudFormation and Python (`boto3`) to manage resources.

## 2. Environment Setup
To ensure the code runs correctly, use the provided virtual environment:

- **Activation Script:** `env_setter.ps1`
- **Venv Path:** `C:\py_venv\aws_playground`
- **Command:** `. .\env_setter.ps1`

This environment contains all necessary dependencies: `boto3`, `cfn-lint`, `PyYAML`, etc.

## 3. Core Components

### CLI Tool (`cli.py`)
The primary entry point for managing the playground.
- **Infrastructure:** `python cli.py infrastructure [deploy|destroy|upload] --stack [network|website|iam|ses]`
- **Audit:** `python cli.py audit [resources|cost]`
- **Pipeline:** `python cli.py pipeline [deploy|upload-job|start-job|...]`
- **AI Agent:** `python cli.py agent ask "your question"`

### Internal Library (`aws_lib/`)
Contains modular logic for different AWS domains:
- `core.py`: Session and authentication management.
- `stacks.py`: CloudFormation deployment logic.
- `audit.py`: Resource and cost auditing.
- `pipeline.py`: Data pipeline (Glue/S3) management.
- `ai.py`: Athena-based data analysis and SQL generation.

### Infrastructure (`infrastructure/`)
CloudFormation templates for:
- VPC Networking
- S3 Static Website
- IAM Users and Policies
- SES Configuration

### Data Pipeline (`cloud_intelligence_pipeline/`)
A working ETL pipeline that:
1. Ingests data (simulated).
2. Processes data using **AWS Glue** (`process_job.py`).
3. Stores output in **Parquet** format in S3 (`egirgis-datalake-v1`).

## 4. Current State (Verified 2026-04-27)
The following checks were performed:

- **CLI Access:** Verified `cli.py` executes correctly in the `study` profile.
- **Cost Audit:** Current month cost is **$0.00**.
- **Resource Audit:** 
    - 1 Lambda function found (`HelloWorldLambda`).
    - No expensive running instances (EC2, RDS, NAT Gateways).
- **Pipeline Status:** 
    - Glue Job `etl-process-orders` status: **SUCCEEDED**.
    - S3 Processed Data: Found 3 Parquet files in `processed/orders_parquet/`.

## 5. Maintenance Notes
- **Encoding:** `check_status.py` was updated to remove emojis that were causing encoding errors in certain terminal environments.
- **Cleanup:** Always use `python cli.py infrastructure destroy` to tear down resources and avoid unexpected costs.
- **S3 Safety:** The `infrastructure destroy` command includes an `empty_bucket` step to ensure CloudFormation can delete S3 buckets.

## 6. Recommended Next Steps
- Explore the **AI Agent** capability by asking questions about the processed data in Athena.
- Continue with **Phase 2 (Observability)** of the roadmap by implementing CloudWatch dashboards.
