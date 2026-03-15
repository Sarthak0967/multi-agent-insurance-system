# =============================================================
# rolling-update.ps1 — Trigger a zero-downtime rolling update
# Usage: .\rolling-update.ps1 -Version v2.0
# =============================================================

param(
  [Parameter(Mandatory=$true)]
  [string]$Version
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Rolling Update → insurance-api:$Version" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Point Docker to Minikube's daemon
Write-Host "[1/4] Switching Docker to Minikube daemon..." -ForegroundColor Yellow
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build the new image version
Write-Host "`n[2/4] Building image insurance-api:$Version ..." -ForegroundColor Yellow
docker build -t "insurance-api:$Version" ./backend
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Build failed." -ForegroundColor Red; exit 1 }

# Trigger rolling update
Write-Host "`n[3/4] Triggering rolling update..." -ForegroundColor Yellow
kubectl set image deployment/insurance-api "insurance-api=insurance-api:$Version"
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: kubectl set image failed." -ForegroundColor Red; exit 1 }

# Watch the rollout
Write-Host "`n[4/4] Watching rollout (zero downtime — maxUnavailable=0)..." -ForegroundColor Yellow
kubectl rollout status deployment/insurance-api --timeout=120s

if ($LASTEXITCODE -eq 0) {
  Write-Host "`n Rolling update to $Version complete!" -ForegroundColor Green
  kubectl get pods
} else {
  Write-Host "`nRollout timed out. Rolling back..." -ForegroundColor Red
  kubectl rollout undo deployment/insurance-api
  Write-Host "Rolled back to previous version." -ForegroundColor Yellow
}