# The Builder: `aws_lib/stacks.py`

## Role
This file is the **Construction Crew**. It knows how to talk to AWS CloudFormation to build infrastructure.

## What it does
It reads the Blueprints (YAML files) and sends them to AWS. It initiates the work and waits for it to finish.

## Key Class: `StackManager`

### Main Functions
1.  **`deploy(stack_name, template_path)`**
    *   This is the "Make it happen" button.
    *   It checks if the stack exists.
    *   It calls `create_stack` or `update_stack` accordingly.
    
2.  **`destroy(stack_name)`**
    *   Tears down the infrastructure for that specific stack.

3.  **`_wait_for_completion(stack_name)`**
    *   This is a helper that puts the script to sleep.
    *   It wakes up every few seconds to ask AWS: "Are you done yet?"
    *   This prevents the script from finishing before the server is actually ready.

4.  **`upload_file(...)`**
    *   A special helper just for the Website.
    *    It takes a local file (`index.html`) and puts it into the S3 Bucket in the cloud.
