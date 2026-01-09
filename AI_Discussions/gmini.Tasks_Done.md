We have built a complete, secure, and professional cloud lab environment from scratch.

Here is the step-by-step summary of our journey today:

### 1. Account Security & Organization

* **Dual-Account Strategy:** We set up your `study` account for learning, keeping it separate from your personal `girgisinv` account.
* **IAM User Creation:** Instead of using the risky Root account, we created a specialized user (`sean-study`) with Administrator permissions for daily work.
* **CLI Profile Mapping:** We configured your Windows 11 machine with multiple AWS profiles (`study`, `girgisinv`, `lab`), allowing you to switch between accounts instantly using the `--profile` flag.

### 2. Network Infrastructure (VPC)

* **Custom VPC Setup:** We scripted the creation of a private network (VPC) with a specific IP range ().
* **Subnetting:** You carved out a "Public Subnet" () within that VPC to hold future servers.
* **Internet Connectivity:** We built and attached an **Internet Gateway** and configured a **Route Table** to allow traffic to flow between your VPC and the open internet.

### 3. Storage & Static Web Hosting (S3)

* **Bucket Creation:** We created a globally unique S3 bucket for your `aws_playground`.
* **Public Access Configuration:** We successfully navigated the "Public Access Block" safety settings to allow your bucket to be web-facing.
* **Website Activation:** You enabled **Static Website Hosting** and configured entry points for `index.html` and `error.html`.
* **Permission Fixes:** We troubleshot and solved complex PowerShell encoding issues (BOM characters) by applying a **Bucket Policy** via the AWS Console to ensure your site is publicly viewable.

### 4. Content Deployment

* **Manual Uploads:** You learned how to use `aws s3 cp` to move files from your local machine to the cloud.
* **Automation:** You successfully tested your custom `error.html` page by visiting a non-existent URL, confirming your S3 routing is working perfectly.

---

### Your Current Status

**Website Live at:** `http://egirg-study-playground-2075671920.s3-website-us-east-1.amazonaws.com`
**CLI Profiles:** Fully configured and verified.

This [AWS VPC Networking guide](https://www.youtube.com/watch?v=aRQgqCTngjw) is relevant because it reinforces the connection between the VPC you built and the S3 bucket policies you just mastered.

**Since your network and storage are ready, would you like to launch that EC2 Linux instance now so you have a real server running inside your new VPC?**