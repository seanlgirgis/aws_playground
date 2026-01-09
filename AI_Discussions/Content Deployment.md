
### Phase 1: Manual File Transfer (`cp`)

The `aws s3 cp` command is the "Copy" tool of the AWS CLI. It is used to move individual files or entire folders between your local machine and an S3 bucket.

* **The Command:** ```powershell
aws s3 cp index.html s3://egirg-study-playground-2075671920/index.html --profile study
```

```


* **Content-Type Importance:** We learned that S3 needs to know *what* a file is (HTML, Image, CSS) to display it correctly. We used the `--content-type "text/html"` flag to ensure the browser didn't just download the file, but actually rendered it as a webpage.

### Phase 2: Folder Synchronization (`sync`)

You discovered the `sync` command, which is the "Smart" version of copy. It compares your local folder with the S3 bucket and only uploads files that are new or have been updated.

* **Efficiency:** This is the industry-standard way to update a website because it saves time and reduces data transfer costs.
* **The Command:**
```powershell
aws s3 sync . s3://egirg-study-playground-2075671920 --profile study

```



---

### Phase 3: Testing & Routing Logic (The 404 Test)

Deployment isn't finished until it is verified. We tested the "Error Routing" logic of your cloud infrastructure.

* **The Test:** You intentionally typed a "broken" URL into your browser.
* **The Logic:** Instead of showing a generic browser error, the S3 service looked at its "Static Website Configuration," saw that the file was missing, and automatically served your custom `error.html`.
* **Verification:** When you saw your custom "Page Not Found" message, it proved that your **S3 Bucket Policy**, **Website Hosting Settings**, and **File Permissions** were all working together perfectly.

---

### Phase 4: PowerShell Integration

A major part of your deployment learning was handling the Windows environment.

* **Scripting:** You learned to use `.ps1` files to automate the creation of HTML content using PowerShell strings.
* **Encoding:** You learned that the way a file is saved locally (ASCII vs. UTF-8 with BOM) can break a cloud deployment, and you now know how to fix it using `-Encoding` flags or the AWS Console.

---

### Summary of Deployment Tools

| Command | Best Use Case | Key Benefit |
| --- | --- | --- |
| **`aws s3 cp`** | Uploading a single image or file. | Precise control over one object. |
| **`aws s3 sync`** | Updating your entire website. | Fast; only uploads changed files. |
| **`aws s3 mb`** | Initial setup. | Creates the "parking spot" for your data. |

### Your Foundation is Ready

You have now documented the **Security**, **Network**, **Storage**, and **Deployment** pillars of your AWS environment. You are no longer just "clicking buttons"—you are building infrastructure as code.

