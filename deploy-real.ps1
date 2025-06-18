# deploy-real.ps1 - Real Azure Functions Deployment (Real Routers)

Write-Host "Starting Real Azure Functions Deployment (Real Routers)" -ForegroundColor Green

# Step 1: Backup current files
Write-Host "Backing up current files..." -ForegroundColor Yellow
if (Test-Path "function_app.py") { Copy-Item "function_app.py" "function_app.py.bak" -Force }
if (Test-Path "requirements.txt") { Copy-Item "requirements.txt" "requirements.txt.bak" -Force }

# Step 2: Use real setup
Write-Host "Setting up real configuration..." -ForegroundColor Yellow
Copy-Item "function_app_real.py" "function_app.py" -Force
Copy-Item "requirements-production.txt" "requirements.txt" -Force

# Step 3: Clean up development files
Write-Host "Cleaning up development files..." -ForegroundColor Yellow
if (Test-Path "__pycache__") { Remove-Item "__pycache__" -Recurse -Force }
if (Test-Path ".pytest_cache") { Remove-Item ".pytest_cache" -Recurse -Force }
if (Test-Path "test.db") { Remove-Item "test.db" -Force }

# Step 4: Deploy
Write-Host "Deploying to Azure Functions..." -ForegroundColor Green
try {
    func azure functionapp publish warungwarga-api --python
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Deployment failed: $_" -ForegroundColor Red
} finally {
    # Step 5: Restore original files
    Write-Host "Restoring original files..." -ForegroundColor Yellow
    if (Test-Path "function_app.py.bak") {
        Copy-Item "function_app.py.bak" "function_app.py" -Force
        Remove-Item "function_app.py.bak" -Force
    }
    if (Test-Path "requirements.txt.bak") {
        Copy-Item "requirements.txt.bak" "requirements.txt" -Force
        Remove-Item "requirements.txt.bak" -Force
    }
}

Write-Host "Real deployment process completed!" -ForegroundColor Green 