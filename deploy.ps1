# =============================================================
# deploy.ps1 - Multi-Agent Insurance System - Full Stack Deploy
# Deploys: FastAPI backend + Streamlit frontend on Minikube
# Run from: D:\dev\projects\multi-agent-insurance\
# =============================================================

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " Insurance AI - Full Stack K8s Deployment" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# STEP 1: Start Minikube
Write-Host "[1/8] Starting Minikube..." -ForegroundColor Yellow
minikube start --driver=docker
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Minikube failed to start." -ForegroundColor Red; exit 1 }

# STEP 2: Point Docker to Minikube daemon
Write-Host "`n[2/8] Switching Docker to Minikube's internal daemon..." -ForegroundColor Yellow
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Could not switch Docker context." -ForegroundColor Red; exit 1 }
Write-Host "Docker is now pointing to Minikube's daemon." -ForegroundColor Green

# STEP 3: Build backend image
Write-Host "`n[3/8] Building backend image (insurance-api:v1.0)..." -ForegroundColor Yellow
docker build -t insurance-api:v1.0 .
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Backend Docker build failed." -ForegroundColor Red; exit 1 }
Write-Host "Backend image built." -ForegroundColor Green

# STEP 4: Build frontend image
Write-Host "`n[4/8] Building frontend image (insurance-frontend:v1.0)..." -ForegroundColor Yellow
docker build -t insurance-frontend:v1.0 -f Dockerfile.frontend .
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Frontend Docker build failed." -ForegroundColor Red; exit 1 }
Write-Host "Frontend image built." -ForegroundColor Green

# STEP 5: Apply ConfigMap + Secret
Write-Host "`n[5/8] Applying ConfigMap and Secret..." -ForegroundColor Yellow
Write-Host "  Make sure k8s/secret.yaml has your real GOOGLE_API_KEY!" -ForegroundColor Magenta
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: ConfigMap/Secret apply failed." -ForegroundColor Red; exit 1 }

# STEP 6: Deploy backend
Write-Host "`n[6/8] Deploying backend (FastAPI + CrewAI agents)..." -ForegroundColor Yellow
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Backend deployment failed." -ForegroundColor Red; exit 1 }

# STEP 7: Deploy frontend
Write-Host "`n[7/8] Deploying frontend (Streamlit)..." -ForegroundColor Yellow
kubectl apply -f k8s/frontend.yaml
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: Frontend deployment failed." -ForegroundColor Red; exit 1 }

# STEP 8: Wait for rollouts
Write-Host "`n[8/8] Waiting for rollouts to complete..." -ForegroundColor Yellow

Write-Host "  Waiting for backend..." -ForegroundColor Gray
kubectl rollout status deployment/insurance-api --timeout=120s
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Backend rollout timed out." -ForegroundColor Red
    Write-Host "Debug with: kubectl get pods" -ForegroundColor Yellow
    Write-Host "Debug with: kubectl logs POD_NAME" -ForegroundColor Yellow
    exit 1
}

Write-Host "  Waiting for frontend..." -ForegroundColor Gray
kubectl rollout status deployment/insurance-frontend --timeout=120s
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Frontend rollout timed out." -ForegroundColor Red
    Write-Host "Debug with: kubectl get pods" -ForegroundColor Yellow
    exit 1
}

# Done
Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  Full Stack Deployment Successful!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "`nKeep this terminal open for the tunnel." -ForegroundColor Magenta

Write-Host "`nBackend API:" -ForegroundColor Yellow
minikube service insurance-api-service --url

Write-Host "`nFrontend (Streamlit UI):" -ForegroundColor Yellow
minikube service insurance-frontend-service --url

Write-Host "`nAll pods:" -ForegroundColor Cyan
kubectl get pods