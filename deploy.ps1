# deploy.ps1 - Production Deployment Script

Write-Host "🚀 Starting Warung Warga API Deployment" -ForegroundColor Green

# Clean up development files
Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
if (Test-Path "__pycache__") { Remove-Item "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path ".pytest_cache") { Remove-Item ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "test.db") { Remove-Item "test.db" -Force -ErrorAction SilentlyContinue }

# Deploy to Azure Functions
Write-Host "🌐 Deploying to Azure Functions..." -ForegroundColor Green
try {
    func azure functionapp publish warungwarga-api --python
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
}

Write-Host "🎉 Deployment process completed!" -ForegroundColor Green 