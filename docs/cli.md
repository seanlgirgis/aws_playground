# The Commander: `cli.py`

## Role
This file is the **Boss** or **Control Center** of the project. It is the only file you need to run directly from your terminal.

## What it does
It acts as a menu system. When you run `python cli.py`, it looks at the extra words you typed (arguments) to decide which "worker" tool to call.

## Commands
It supports two main commands:

### 1. Infrastructure (`handle_infrastructure`)
Used to build or destroy your cloud setup.
*   **`deploy`**: Builds the Network (VPC) and the Website (S3).
*   **`destroy`**: Tears everything down (empties bucket and deletes stacks).
*   **`upload`**: Updates just the `index.html` file without touching the infrastructure.

### 2. Audit (`handle_audit`)
Used to check your account status.
*   **`resources`**: Checks for running servers or unattached hard drives.
*   **`cost`**: checks your AWS bill for the current month.

## Key Concept
It heavily relies on `Matchmaking`. It matches your command (e.g., "deploy") to the right function in `stacks.py`. It doesn't know *how* to build a VPC, it just knows *who* to ask (the StackManager).
