# Cloud Intelligence Pipeline

**Objective:** A Serverless Data Lake + AI Agent on AWS.

## Architecture
1.  **S3:** Data Lake Storage (Raw & Processed).
2.  **Glue:** Serverless Spark ETL.
3.  **Athena:** SQL Query Engine.
4.  **Bedrock:** AI Agent (Text-to-SQL).

## Setup
1.  Configure AWS Credentials (`aws configure`).
2.  Run `scripts/00_setup.py` (to be created) to provision S3 buckets.
