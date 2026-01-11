$Env:AWS_PROFILE = "study"
$VPC_NAME = "Playground-VPC"

# 1. Check if the VPC already exists, if not, create it
Write-Host "Checking for VPC: $VPC_NAME..." -ForegroundColor Cyan
$VPC_ID = aws ec2 describe-vpcs --filters "Name=tag:Name,Values=$VPC_NAME" --query "Vpcs[0].VpcId" --output text

if ($VPC_ID -eq "None" -or -not $VPC_ID) {
    Write-Host "VPC not found. Creating new VPC..." -ForegroundColor Yellow
    $VPC_ID = aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$VPC_NAME}]" --query 'Vpc.VpcId' --output text
}
Write-Host "Using VPC: $VPC_ID" -ForegroundColor Green

# 2. Create a Public Subnet
Write-Host "Creating Subnet..." -ForegroundColor Cyan
$SUBNET_ID = aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --query 'Subnet.SubnetId' --output text

# 3. Create and Attach an Internet Gateway
Write-Host "Creating Internet Gateway..." -ForegroundColor Cyan
$IGW_ID = aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

# 4. Create a Route Table and a Route to the Internet
Write-Host "Setting up Routing..." -ForegroundColor Cyan
$RT_ID = aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text
aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --subnet-id $SUBNET_ID --route-table-id $RT_ID

Write-Host "--- Setup Complete ---" -ForegroundColor Green
Write-Host "VPC: $VPC_ID | Subnet: $SUBNET_ID | IGW: $IGW_ID" -ForegroundColor Green