### Phase 1: The Bucket (Global Storage)

S3 (Simple Storage Service) is an object storage service. Unlike a folder on your computer, every S3 bucket name must be **globally unique** because it forms part of a URL.

* **The Command:** ```powershell
aws s3 mb s3://egirg-study-playground-2075671920
```
* `mb` stands for "Make Bucket."
* Once created, this bucket exists in the **us-east-1** region but is reachable from anywhere in the world.


```



### Phase 2: Opening the "Safety Locks"

By default, AWS applies **Public Access Blocks** to every new bucket to prevent data leaks. Even if you have a "Public" policy, these blocks act as a master override.

* **What we did:** We disabled these blocks so the bucket could officially "see" the public internet.
* **The Logic:** You turned off four specific settings that prevent public ACLs and Policies from taking effect.

---

### Phase 3: Enabling Website Mode

Standard S3 buckets serve files as "downloads." To make them behave like a website (rendering HTML in a browser), you must enable **Static Website Hosting**.

* **The Configuration:** You told S3 that whenever someone visits the root URL, it should look for `index.html`.
* **Error Handling:** You designated `error.html` as the file to show if a user requests a page that doesn't exist (the 404 error).
* **The Result:** This created your **Website Endpoint**: `http://bucket-name.s3-website-region.amazonaws.com`.

### Phase 4: The Bucket Policy (Permissions)

This was the most critical step. A **Bucket Policy** is a JSON document that defines who can do what.

* **The Policy:** You applied a "Public Read" policy. It tells AWS: *"Allow any Principal (everyone) to perform the Action 's3:GetObject' (viewing) on every file inside this bucket."*
* **The Troubleshooting:** We discovered that PowerShell 5.1 adds a hidden **Byte Order Mark (BOM)** to files. AWS CLI rejected the policy because it didn't start with a clean `{` byte. We bypassed this by pasting the JSON directly into the AWS Console.

---

### Summary of the "Public" Layers

For your website to work, **all three** of these layers had to be aligned:

| Layer | Purpose | Status |
| --- | --- | --- |
| **Public Access Block** | The Master "Safety" Switch | **OFF** |
| **Bucket Policy** | The "Who can see what" rules | **ALLOW ALL** |
| **Object Metadata** | Ensures files are read as "HTML" | **text/html** |

### Key Takeaway for your Learning

You learned that **Cloud Security is layered**. Just because you "turn on" a website doesn't mean it's viewable; you have to intentionally grant permission at the account level (Blocks), the bucket level (Policy), and the object level (Content-Type).

