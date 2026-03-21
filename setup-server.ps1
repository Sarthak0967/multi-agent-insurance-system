# =============================================================
# setup-server.ps1 - Install Docker + Deploy app on EC2
# Run AFTER launch-ec2.ps1 from project root
# Requires: insurance-app-key.pem + ec2-info.json
# =============================================================

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " Setting Up EC2 Server + Deploying App" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# ── Load EC2 info ─────────────────────────────────────────────
if (-not (Test-Path "ec2-info.json")) {
    Write-Host "ERROR: ec2-info.json not found. Run launch-ec2.ps1 first." -ForegroundColor Red; exit 1
}
$ec2 = Get-Content "ec2-info.json" | ConvertFrom-Json
$PUBLIC_IP = $ec2.PublicIP
$KEY_FILE  = $ec2.KeyFile

Write-Host "Target server : $PUBLIC_IP" -ForegroundColor Cyan
Write-Host "Key file      : $KEY_FILE`n" -ForegroundColor Cyan

# ── Fix key file permissions (Windows SSH requirement) ────────
Write-Host "[1/4] Fixing key file permissions..." -ForegroundColor Yellow
icacls $KEY_FILE /inheritance:r /grant:r "${env:USERNAME}:R" | Out-Null
Write-Host "Done." -ForegroundColor Green

# ── Read Gemini API key ───────────────────────────────────────
Write-Host "`n[2/4] Enter your Gemini API key:" -ForegroundColor Yellow
$GOOGLE_API_KEY = Read-Host "GOOGLE_API_KEY"
if (-not $GOOGLE_API_KEY) {
    Write-Host "ERROR: API key cannot be empty." -ForegroundColor Red; exit 1
}

# ── Create the setup script to run on EC2 ────────────────────
Write-Host "`n[3/4] Preparing server setup script..." -ForegroundColor Yellow

$setupScript = @"
#!/bin/bash
set -e

echo '========================================'
echo ' Installing Docker on Ubuntu...'
echo '========================================'

# Update system
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release git

# Install Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker

echo 'Docker installed successfully!'
docker --version

echo '========================================'
echo ' Uploading project files...'
echo '========================================'
mkdir -p /home/ubuntu/insurance-app

echo '========================================'
echo ' Creating .env file...'
echo '========================================'
cat > /home/ubuntu/insurance-app/.env << 'ENVEOF'
GOOGLE_API_KEY=$GOOGLE_API_KEY
ENVEOF

echo 'Setup complete! Ready for file upload.'
"@

$setupScript | Out-File -FilePath "ec2-setup.sh" -Encoding UTF8 -NoNewline

# ── Wait for SSH to be ready ──────────────────────────────────
Write-Host "`n[4/4] Waiting for SSH to be ready on server..." -ForegroundColor Yellow
$maxAttempts = 20
$attempt = 0
do {
    Start-Sleep -Seconds 10
    $attempt++
    Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    $result = ssh -i $KEY_FILE -o "StrictHostKeyChecking=no" -o "ConnectTimeout=5" "ubuntu@$PUBLIC_IP" "echo ready" 2>$null
} while ($result -ne "ready" -and $attempt -lt $maxAttempts)

if ($result -ne "ready") {
    Write-Host "ERROR: Could not connect to server. Wait 2 minutes and retry." -ForegroundColor Red; exit 1
}
Write-Host "SSH connection established!" -ForegroundColor Green

# ── Run setup script on server ────────────────────────────────
Write-Host "`nRunning Docker installation on server (2-3 minutes)..." -ForegroundColor Yellow
scp -i $KEY_FILE -o "StrictHostKeyChecking=no" "ec2-setup.sh" "ubuntu@${PUBLIC_IP}:/home/ubuntu/setup.sh"
ssh -i $KEY_FILE -o "StrictHostKeyChecking=no" "ubuntu@$PUBLIC_IP" "chmod +x /home/ubuntu/setup.sh && /home/ubuntu/setup.sh"

# ── Upload project files ──────────────────────────────────────
Write-Host "`nUploading project files to server..." -ForegroundColor Yellow

# Upload Dockerfiles
scp -i $KEY_FILE -o "StrictHostKeyChecking=no" "Dockerfile" "ubuntu@${PUBLIC_IP}:/home/ubuntu/insurance-app/"
scp -i $KEY_FILE -o "StrictHostKeyChecking=no" "Dockerfile.frontend" "ubuntu@${PUBLIC_IP}:/home/ubuntu/insurance-app/"
scp -i $KEY_FILE -o "StrictHostKeyChecking=no" "docker-compose.prod.yml" "ubuntu@${PUBLIC_IP}:/home/ubuntu/insurance-app/docker-compose.yml"
scp -i $KEY_FILE -o "StrictHostKeyChecking=no" "streamlit_app.py" "ubuntu@${PUBLIC_IP}:/home/ubuntu/insurance-app/"

# Upload backend folder
scp -i $KEY_FILE -o "StrictHostKeyChecking=no" -r "backend" "ubuntu@${PUBLIC_IP}:/home/ubuntu/insurance-app/"

Write-Host "Files uploaded!" -ForegroundColor Green

# ── Build and start containers ────────────────────────────────
Write-Host "`nBuilding Docker images and starting containers..." -ForegroundColor Yellow
Write-Host "(This takes 3-5 minutes on first run)" -ForegroundColor Gray

ssh -i $KEY_FILE -o "StrictHostKeyChecking=no" "ubuntu@$PUBLIC_IP" @"
cd /home/ubuntu/insurance-app
sudo docker compose up -d --build
echo 'Containers started!'
sudo docker ps
"@

# ── Done ──────────────────────────────────────────────────────
Write-Host "`n============================================" -ForegroundColor Green
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "`nYour app is live at:" -ForegroundColor Cyan
Write-Host "  Backend API  : http://${PUBLIC_IP}:8000/api/system/health" -ForegroundColor White
Write-Host "  Streamlit UI : http://${PUBLIC_IP}:8501" -ForegroundColor White
Write-Host "`nSSH into server anytime:" -ForegroundColor Cyan
Write-Host "  ssh -i $KEY_FILE ubuntu@$PUBLIC_IP" -ForegroundColor White
Write-Host "`nTo stop everything (avoid charges):" -ForegroundColor Yellow
Write-Host "  .\destroy-ec2.ps1" -ForegroundColor White