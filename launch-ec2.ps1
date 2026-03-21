# =============================================================
# launch-ec2.ps1 - Launch EC2 instance for Insurance App
# Run from: D:\dev\projects\multi-agent-insurance\
# Region: ap-south-1 (Mumbai)
# =============================================================

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " Launching EC2 Instance - Insurance App" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$REGION = "ap-south-1"
$KEY_NAME = "insurance-app-key"
$SG_NAME = "insurance-app-sg"
$INSTANCE_NAME = "insurance-app-server"

# Find free tier eligible instance type for this account/region
Write-Host "[0/5] Finding free tier instance type for your account..." -ForegroundColor Yellow
$FREE_INSTANCE = aws ec2 describe-instance-types `
    --filters "Name=free-tier-eligible,Values=true" `
    --region $REGION `
    --query "InstanceTypes[0].InstanceType" `
    --output text

if (-not $FREE_INSTANCE -or $FREE_INSTANCE -eq "None") {
    Write-Host "No free tier found, using t3.micro (~$0.01/hr)..." -ForegroundColor Yellow
    $FREE_INSTANCE = "t3.micro"
}
Write-Host "Using instance type: $FREE_INSTANCE" -ForegroundColor Green

# Get latest Ubuntu 22.04 AMI for ap-south-1
Write-Host "`nFinding latest Ubuntu 22.04 AMI..." -ForegroundColor Yellow
$AMI_ID = aws ec2 describe-images `
    --owners 099720109477 `
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" `
              "Name=state,Values=available" `
    --region $REGION `
    --query "sort_by(Images, &CreationDate)[-1].ImageId" `
    --output text

Write-Host "Using AMI: $AMI_ID" -ForegroundColor Green

# ── STEP 1: Key pair already created - skip ───────────────────
Write-Host "`n[1/5] Key pair already exists: $KEY_NAME.pem" -ForegroundColor Green

# ── STEP 2: Security group already created ────────────────────
Write-Host "`n[2/5] Security group already exists: $SG_NAME" -ForegroundColor Green
$SG_ID = aws ec2 describe-security-groups `
    --filters "Name=group-name,Values=$SG_NAME" `
    --region $REGION `
    --query "SecurityGroups[0].GroupId" `
    --output text

Write-Host "Security Group ID: $SG_ID" -ForegroundColor Cyan

# ── STEP 3: Launch EC2 Instance ───────────────────────────────
Write-Host "`n[3/5] Launching EC2 instance ($FREE_INSTANCE)..." -ForegroundColor Yellow

$INSTANCE_ID = aws ec2 run-instances `
    --image-id $AMI_ID `
    --instance-type $FREE_INSTANCE `
    --key-name $KEY_NAME `
    --security-group-ids $SG_ID `
    --region $REGION `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" `
    --query "Instances[0].InstanceId" `
    --output text

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to launch instance." -ForegroundColor Red; exit 1
}
Write-Host "Instance launched: $INSTANCE_ID" -ForegroundColor Green

# ── STEP 4: Wait for instance to be running ───────────────────
Write-Host "`n[4/5] Waiting for instance to start (60-90 seconds)..." -ForegroundColor Yellow
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION
Write-Host "Instance is running!" -ForegroundColor Green

# ── STEP 5: Get Public IP ─────────────────────────────────────
Write-Host "`n[5/5] Getting public IP address..." -ForegroundColor Yellow
$PUBLIC_IP = aws ec2 describe-instances `
    --instance-ids $INSTANCE_ID `
    --region $REGION `
    --query "Reservations[0].Instances[0].PublicIpAddress" `
    --output text

# Save instance info
$info = @{
    InstanceId = $INSTANCE_ID
    PublicIP   = $PUBLIC_IP
    Region     = $REGION
    KeyFile    = "$KEY_NAME.pem"
}
$info | ConvertTo-Json | Out-File -FilePath "ec2-info.json" -Encoding UTF8

# ── Done ──────────────────────────────────────────────────────
Write-Host "`n============================================" -ForegroundColor Green
Write-Host " EC2 Instance Ready!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "`nInstance ID : $INSTANCE_ID" -ForegroundColor Cyan
Write-Host "Public IP   : $PUBLIC_IP" -ForegroundColor Cyan
Write-Host "Key file    : $KEY_NAME.pem" -ForegroundColor Cyan
Write-Host "`nNext step - run: .\setup-server.ps1" -ForegroundColor Yellow