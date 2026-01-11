# The Key Master: `aws_lib/core.py`

## Role
This file handles **Authentication** and **Security**. It is the "Bouncer" at the door.

## What it does
Before any other code can talk to AWS, it needs permission. This file finds your AWS credentials (keys) and creates a `Session`.

## Key Class: `SessionManager`
*   **`get_session(profile_name)`**: This is the main function.
    1.  It looks for a `profile_name` (like "default" or "study").
    2.  It uses the `boto3` library to unlock that profile.
    3.  It returns a **Session Object** (The Security Badge).

## Why it is separate?
By keeping authentication in one place:
1.  We don't have to write "login code" in every single file.
2.  If we change how we login (e.g., adding MFA), we only change it here.
