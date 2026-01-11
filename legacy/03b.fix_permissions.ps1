$Env:AWS_PROFILE = "study"
$BUCKET = "egirg-study-playground-2075671920"

Write-Host "Force-fixing permissions for $BUCKET..." -ForegroundColor Cyan

# 1. Turn off all public access blocks for this bucket
aws s3api put-public-access-block `
    --bucket $BUCKET `
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# 2. Re-apply the Public Read Policy
# (Sometimes the policy fails if the block above was still active)
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
'@ -replace "BUCKET_NAME", $BUCKET

$policy | Out-File -FilePath temp_policy.json -Encoding utf8
aws s3api put-bucket-policy --bucket $BUCKET --policy file://temp_policy.json

Remove-Item temp_policy.json
Write-Host "Permissions Updated! Refresh your browser in 10 seconds." -ForegroundColor Green