# --- 1. SET THE PROFILE ---
$Env:AWS_PROFILE = "study"

# --- 2. CREATE S3 BUCKET ---
# Replace 'egirg-study-bucket-2026' with a unique name of your choice
$BUCKET_NAME = "egirg-study-playground-$(Get-Random)"

Write-Host "Creating Bucket: $BUCKET_NAME..." -ForegroundColor Cyan
aws s3 mb "s3://$BUCKET_NAME"

# --- 3. CREATE A VPC ---
Write-Host "Creating VPC..." -ForegroundColor Cyan
$VPC_ID = aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text

Write-Host "Successfully created VPC: $VPC_ID" -ForegroundColor Green
Write-Host "Successfully created Bucket: $BUCKET_NAME" -ForegroundColor Green