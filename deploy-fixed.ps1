# deploy-fixed.ps1 - Fixed Azure Functions Deployment

Write-Host "Starting Fixed Azure Functions Deployment" -ForegroundColor Green

# Step 1: Backup current files
Write-Host "Backing up current files..." -ForegroundColor Yellow
if (Test-Path "function_app.py") { Copy-Item "function_app.py" "function_app.py.bak" -Force }

# Step 2: Use fixed setup
Write-Host "Setting up fixed configuration..." -ForegroundColor Yellow
Copy-Item "function_app_fixed.py" "function_app.py" -Force

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
}

Write-Host "Fixed deployment process completed!" -ForegroundColor Green 