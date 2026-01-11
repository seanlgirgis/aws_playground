# AWS Learning Roadmap

You have a robust foundation: **VPC** (Networking) and **S3** (Storage). 
To truly master AWS, we will build "Modules" on top of this. Each module will introduce a core concept, implement it via CloudFormation, and control it via your Python library.

## Phase 1: The Core Services (Compute & Security)

### Module 1: IAM & Security (The Backbone)
*   **Concept**: Users, Groups, Roles, and Policies. Least Privilege.
*   **Build**: Create a custom IAM Role for an EC2 instance to access your S3 bucket (without hardcoded keys!).
*   **Code**: `aws_lib/iam.py`

### Module 2: EC2 (Virtual Servers)
*   **Concept**: Instances, AMIs, Key Pairs, Security Groups (Firewalls).
*   **Build**: Launch a Linux web server in your Public Subnet. SSH into it. Install Apache.
*   **Code**: `aws_lib/ec2.py` (Start/Stop/Audit instances).

## Phase 2: Modern Application Architecture

### Module 3: Serverless Compute (Lambda)
*   **Concept**: "Functions as a Service". No server management.
*   **Build**: A Python function that triggers whenever a file is uploaded to your S3 bucket (e.g., to resize an image or log metadata).
*   **Code**: `aws_lib/lambda.py`

### Module 4: Databases (DynamoDB)
*   **Concept**: NoSQL single-digit millisecond latency.
*   **Build**: A "Guestbook" table for your website.
*   **Code**: `aws_lib/dynamo.py`

## Phase 3: Traffic Management

### Module 5: Load Balancing (ALB) & Auto Scaling
*   **Concept**: High Availability.
*   **Build**: Put your EC2 instances behind a Load Balancer so if one fails, the site stays up.

---

## Recommended Next Step
**Module 1 (IAM)** or **Module 2 (EC2)**.
*   **IAM** is crucial for doing EC2 correctly (assigning permissions to the server).
*   **EC2** is more "fun" (you get a real server to hack on).
