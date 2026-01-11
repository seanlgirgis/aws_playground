# AWS Cloud Data & AI Engineering Playground

## 🎯 Mission Statement
To master the end-to-end lifecycle of modern cloud engineering, bridging the gap between **Infrastructure**, **Data**, and **Artificial Intelligence**. 

This project is not just a collection of scripts; it is a rigorous training ground to develop the skills required for the roles of:
*   **Data Engineer** (Building robust pipelines)
*   **AI/ML Developer** (Deploying intelligent models)
*   **Cloud Developer** (Automating infrastructure)
*   **Observability Engineer** (Monitoring health and costs)

 > [!TIP]
 > New to AWS? Start by reading our [AWS Ecosystem Essentials](education/aws_essentials.md) guide to understand Regions, Security, and Core Services.

## 🏗️ Methodology
We adhere to the philosophy of **"Infrastructure as Code" (IaC)**. Nothing is created manually.
1.  **Define**: distinct resources in CloudFormation/Python.
2.  **Deploy**: via our custom CLI (`aws_lib`).
3.  **Audit**: costs and resources programmatically.
4.  **Destroy**: to maintain zero/low cost when not in use.

## 🎓 Training Curriculum / Roadmap

### Phase 1: Foundation (Cloud Developer) ✅
*   [x] **Infrastructure as Code**: Managing VPCs and S3 via Python `boto3` & CloudFormation.
*   [x] **Cost & Resource Control**: Automated auditing mechanisms.
*   [ ] **Identity & Security (IAM)**: Implementing Least Privilege for machines and humans.

### Phase 2: Observability & Monitoring 👁️
*   **Goal**: "If you can't measure it, you can't manage it."
*   **Modules**:
    *   **CloudWatch**: Custom metrics and dashboards.
    *   **EventBridge**: Reacting to system events in real-time.
    *   **AWS Config**: Compliance auditing.

### Phase 3: Data Engineering (The Pipelines)  pipelines
*   **Goal**: Moving and transforming data at scale.
*   **Modules**:
    *   **Lambda (Serverless)**: Event-driven data processing.
    *   **Glue & Athena**: Serverless ETL and SQL querying of S3 data.
    *   **Kinesis**: Real-time data streaming.

### Phase 4: Data Science & AI 🤖
*   **Goal**: Extracting value and intelligence from data.
*   **Modules**:
    *   **SageMaker**: Training and deploying ML models.
    *   **Bedrock**: Integrating Generative AI (LLMs) into applications.
    *   **QuickSight**: Visualizing insights.

## 🛠️ Usage
This learning environment is controlled via the `cli.py` tool:

```bash
# Manage Infrastructure
python cli.py infrastructure [deploy|destroy|upload]

# Audit Setup
python cli.py audit [resources|cost]
```
