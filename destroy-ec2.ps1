# =============================================================
# destroy-ec2.ps1 - Terminate EC2 instance to avoid charges
# Run from: D:\dev\projects\multi-agent-insurance\
# =============================================================

Write-Host "`n============================================" -ForegroundColor Red
Write-Host " Destroying EC2 Instance (stop charges)" -ForegroundColor Red
Write-Host "============================================`n" -ForegroundColor Red

if (-not (Test-Path "ec2-info.json")) {
    Write-Host "ERROR: ec2-info.json not found." -ForegroundColor Red; exit 1
}

$ec2 = Get-Content "ec2-info.json" | ConvertFrom-Json
$INSTANCE_ID = $ec2.InstanceId
$REGION = $ec2.Region

Write-Host "Instance to terminate: $INSTANCE_ID" -ForegroundColor Yellow
$confirm = Read-Host "Type YES to confirm termination"

if ($confirm -ne "YES") {
    Write-Host "Cancelled." -ForegroundColor Gray; exit 0
}

aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION | Out-Null
Write-Host "Instance $INSTANCE_ID terminating..." -ForegroundColor Yellow

aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID --region $REGION
Write-Host "Instance terminated. No more charges." -ForegroundColor Green

# Clean up local files
Remove-Item "ec2-info.json" -ErrorAction SilentlyContinue
Remove-Item "ec2-setup.sh" -ErrorAction SilentlyContinue

Write-Host "`nTo redeploy fresh: .\launch-ec2.ps1" -ForegroundColor Cyan