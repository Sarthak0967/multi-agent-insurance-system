# =============================================================
# start.ps1 - Multi-Agent Insurance System - Daily Start
# Use this AFTER the first deployment is done.
# Run from: D:\dev\projects\multi-agent-insurance\
# =============================================================

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " Insurance AI - Starting Existing Cluster" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# STEP 1: Start Minikube (resumes existing cluster, no rebuild)
Write-Host "[1/3] Starting Minikube cluster..." -ForegroundColor Yellow
minikube start --driver=docker
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Minikube failed to start." -ForegroundColor Red; exit 1 }
Write-Host "Cluster is up." -ForegroundColor Green

# STEP 2: Check all pods come back healthy
Write-Host "`n[2/3] Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/insurance-api --timeout=120s
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Backend did not come up. Run: kubectl get pods" -ForegroundColor Red; exit 1 }
kubectl rollout status deployment/insurance-frontend --timeout=120s
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Frontend did not come up. Run: kubectl get pods" -ForegroundColor Red; exit 1 }

# STEP 3: Open tunnels to both services
Write-Host "`n[3/3] Opening service tunnels..." -ForegroundColor Yellow
Write-Host "Keep this terminal open!" -ForegroundColor Magenta

Write-Host "`nBackend API:" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "minikube service insurance-api-service --url"

Write-Host "Frontend (Streamlit UI):" -ForegroundColor Yellow
minikube service insurance-frontend-service --url

Write-Host "`nAll pods:" -ForegroundColor Cyan
kubectl get pods