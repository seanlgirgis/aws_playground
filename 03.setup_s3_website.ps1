# ---------------------------------------------------------------------------
# SCRIPT: 03.setup_s3_website.ps1
# PURPOSE: Configures an S3 bucket to act as a public web server.
# PREREQUISITES: A unique S3 bucket name created in previous steps.
# ---------------------------------------------------------------------------

# 1. Configuration Variables
$Env:AWS_PROFILE = "study"
$BUCKET_NAME = "egirg-study-playground-2075671920" # <--- Ensure this is your correct bucket name
$REGION = "us-east-1"

Write-Host "--- Starting S3 Website Deployment for: $BUCKET_NAME ---" -ForegroundColor Cyan

# 2. Create the index.html file locally
# This is the "Home Page" of your website.
$htmlContent = "<html><body style='font-family:sans-serif; text-align:center;'><h1>Success!</h1><p>Hosted on Amazon S3 via PowerShell CLI.</p></body></html>"
$htmlContent | Out-File -FilePath index.html -Encoding utf8
Write-Host "[1/5] Created local index.html file." -ForegroundColor White

# 3. Upload the file to S3
# We upload the file first. By default, it will be private.
aws s3 cp index.html "s3://$BUCKET_NAME/index.html"
Write-Host "[2/5] Uploaded index.html to S3." -ForegroundColor White

# 4. Remove Public Access Block
# AWS accounts have a "Master Switch" that blocks public buckets for safety.
# We must turn off two specific blocks to allow our Policy to work.
Write-Host "[3/5] Disabling Public Access Blocks for this bucket..." -ForegroundColor White
aws s3api put-public-access-block `
    --bucket $BUCKET_NAME `
    --public-access-block-configuration "BlockPublicPolicy=false,RestrictPublicBuckets=false"

# 5. Apply the Bucket Policy (The "Permissions" Layer)
# This JSON tells AWS: "Allow anyone (*) to perform 's3:GetObject' on everything inside this bucket."
$policy = @'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::BUCKET_NAME/*"
        }
    ]
}
'@ -replace "BUCKET_NAME", $BUCKET_NAME

# Save the policy to a temp file and apply it
$policy | Out-File -FilePath policy.json -Encoding utf8
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://policy.json
Write-Host "[4/5] Applied Public Read Policy." -ForegroundColor White

# 6. Enable Static Website Hosting
# This tells S3 to treat the bucket like a web server instead of just a storage folder.
aws s3 website "s3://$BUCKET_NAME/" --index-document index.html
Write-Host "[5/5] Static Website Hosting enabled." -ForegroundColor White

# 7. Provide the final URL
$url = "http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
Write-Host "`n--- DEPLOYMENT COMPLETE ---" -ForegroundColor Green
Write-Host "View your website here: $url" -ForegroundColor Yellow

# Clean up local temporary files
Remove-Item policy.json