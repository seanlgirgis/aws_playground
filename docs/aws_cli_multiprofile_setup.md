---
title: AWS CLI Multi-Profile Setup & Management
created: 2026-01-26
tags: [aws, cli, setup, windows, powershell]
category: Resources/AWS
---

# AWS CLI: Multi-Profile Setup & Management (Windows 11)

To set up multiple AWS CLI profiles, you use the `aws configure --profile <name>` command to store separate credentials and settings for different accounts.

Here is a detailed breakdown of the setup.

## Phase 1: Create Programmatic Access (Generic Steps)

Before touching the CLI, you must generate the "Keys" in the AWS Console for the specific user you want to use.

## Phase 2: Map the Profile to your Windows 11 CLI

In your PowerShell terminal, instead of just running `aws configure` (which overwrites your "default" account), add a profile name.

### The Command

```powershell
aws configure --profile study
```

The CLI will prompt you for four pieces of information:
1.  AWS Access Key ID
2.  AWS Secret Access Key
3.  Default region name (e.g., `us-east-1`)
4.  Default output format (e.g., `json`)

## Phase 3: File Storage Location

On Windows 11, AWS stores these details in your user folder at `C:\Users\YourName\.aws\`. It creates two specific files:

-   `credentials`: Stores your sensitive keys.
-   `config`: Stores non-sensitive settings like region.

## Phase 4: Using the Profiles

Once configured, you have two ways to tell AWS which profile to use:

### Method A: The Flag (Best for one-off commands)
Append `--profile <name>` to any command.

```powershell
aws s3 ls --profile study
```

### Method B: The Session Variable (Best for long work sessions)
Tell PowerShell to use one profile for every command in the current window.

```powershell
$Env:AWS_PROFILE = "study"
aws s3 ls  # No --profile flag needed now!
```
