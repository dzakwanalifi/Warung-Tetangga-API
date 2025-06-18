# deploy.ps1 - Azure Functions Deployment Script

Write-Host "🚀 Starting Azure Functions Deployment for Warung Warga API" -ForegroundColor Green

# Step 1: Clean up development files
Write-Host "🧹 Cleaning up development files..." -ForegroundColor Yellow
if (Test-Path "test.db") { Remove-Item "test.db" -Force }
if (Test-Path "__pycache__") { Remove-Item "__pycache__" -Recurse -Force }
if (Test-Path ".pytest_cache") { Remove-Item ".pytest_cache" -Recurse -Force }
if (Test-Path "test_*.py") { Remove-Item "test_*.py" -Force }

# Step 2: Backup current requirements.txt
Write-Host "💾 Backing up requirements.txt..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Copy-Item "requirements.txt" "requirements-full.txt.bak"
}

# Step 3: Use production requirements
Write-Host "📦 Using production requirements..." -ForegroundColor Yellow
if (Test-Path "requirements-production.txt") {
    Copy-Item "requirements-production.txt" "requirements.txt" -Force
}

# Step 4: Deploy to Azure Functions
Write-Host "🌐 Deploying to Azure Functions..." -ForegroundColor Green
try {
    func azure functionapp publish warung-warga-api --python
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
} finally {
    # Step 5: Restore original requirements.txt
    Write-Host "🔄 Restoring original requirements.txt..." -ForegroundColor Yellow
    if (Test-Path "requirements-full.txt.bak") {
        Copy-Item "requirements-full.txt.bak" "requirements.txt" -Force
        Remove-Item "requirements-full.txt.bak" -Force
    }
}

Write-Host "✅ Deployment process completed!" -ForegroundColor Green 