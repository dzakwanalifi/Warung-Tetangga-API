# deploy-working.ps1 - Working Azure Functions Deployment (Minimal FastAPI)

Write-Host "Starting Working Azure Functions Deployment (Minimal)" -ForegroundColor Green

# Step 1: Backup current files
Write-Host "Backing up current files..." -ForegroundColor Yellow
if (Test-Path "function_app.py") { Copy-Item "function_app.py" "function_app.py.bak" -Force }
if (Test-Path "requirements.txt") { Copy-Item "requirements.txt" "requirements.txt.bak" -Force }

# Step 2: Use working setup
Write-Host "Setting up working configuration..." -ForegroundColor Yellow
Copy-Item "function_app_working.py" "function_app.py" -Force
Copy-Item "requirements-working.txt" "requirements.txt" -Force

# Step 3: Deploy
Write-Host "Deploying to Azure Functions..." -ForegroundColor Green
try {
    func azure functionapp publish warungwarga-api --python
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Deployment failed: $_" -ForegroundColor Red
} finally {
    # Step 4: Restore original files
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

Write-Host "Working deployment process completed!" -ForegroundColor Green 