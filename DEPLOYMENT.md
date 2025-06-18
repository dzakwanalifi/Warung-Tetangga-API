# 🚀 Deployment Guide - Warung Warga API

**Production-Ready FastAPI Backend untuk Hyperlocal Marketplace**

## 📋 Prerequisites

### Required Services & Accounts
- ✅ **GitHub Account** (untuk repository)
- ✅ **Azure Account** (untuk hosting & blob storage)
- ✅ **Supabase Account** (untuk database & auth)
- ✅ **Tripay Account** (untuk payment gateway)
- ✅ **Google Cloud** (untuk Gemini AI)

### Domain Requirements
- Custom domain (recommended)
- SSL certificate (auto-provisioned via Azure)

---

## 🏗️ Infrastructure Architecture

```
Frontend (Vercel/Netlify)
    ↓ HTTPS API Calls
Backend API (Azure Functions/App Service)
    ↓ Database Queries
PostgreSQL (Supabase)
    ↓ File Storage
Azure Blob Storage
    ↓ External Services
[Tripay] [Google Gemini] [Supabase Auth]
```

---

## 🔧 Environment Configuration

### 1. Database Setup (Supabase)
```bash
# Supabase Project Settings
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@host:5432/database
```

### 2. Azure Blob Storage
```bash
# Azure Storage Account
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER_NAME=lapak-images
```

### 3. Payment Gateway (Tripay)
```bash
# Tripay Configuration
TRIPAY_API_KEY=your-api-key
TRIPAY_PRIVATE_KEY=your-private-key
TRIPAY_MERCHANT_CODE=your-merchant-code
TRIPAY_MODE=sandbox  # atau 'production'
```

### 4. AI Integration (Google Gemini)
```bash
# Google AI Studio
GOOGLE_AI_API_KEY=your-gemini-api-key
```

### 5. Security & CORS
```bash
# Application Settings
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_ORIGINS=["https://yourdomain.com", "http://localhost:3000"]
```

---

## ☁️ Deployment Options

### Option 1: Azure App Service (Recommended)

#### Step 1: Create Azure App Service
```bash
# Azure CLI Commands
az webapp create \
  --resource-group Warung-Warga-rg \
  --plan Warung-Warga-plan \
  --name Warung-Warga-api \
  --runtime "PYTHON|3.11"
```

#### Step 2: Configure Environment Variables
```bash
# Set environment variables via Azure Portal atau CLI
az webapp config appsettings set \
  --resource-group Warung-Warga-rg \
  --name Warung-Warga-api \
  --settings \
    DATABASE_URL="your-database-url" \
    SUPABASE_URL="your-supabase-url" \
    # ... (semua environment variables)
```

#### Step 3: Deploy via GitHub Actions
```yaml
# .github/workflows/deploy.yml (sudah tersedia)
name: Deploy to Azure App Service
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Deploy to Azure
        uses: azure/webapps-deploy@v2
        with:
          app-name: 'Warung-Warga-api'
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

### Option 2: Azure Functions (Serverless)

#### Advantages
- ✅ Auto-scaling
- ✅ Pay-per-execution
- ✅ Built-in monitoring
- ✅ Easy CI/CD integration

#### Configuration
```python
# function_app.py
import azure.functions as func
from app.main import app

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.AsgiMiddleware(app).handle(req, context)
```

### Option 3: Docker Container

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose (Development)
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
    env_file:
      - .env
```

---

## 🔒 Security Checklist

### Pre-Deployment Security
- ✅ All secrets stored in environment variables
- ✅ No hardcoded API keys in code
- ✅ HTTPS enforced for all endpoints
- ✅ CORS properly configured
- ✅ JWT tokens with reasonable expiration
- ✅ Input validation on all endpoints
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ File upload restrictions implemented

### Post-Deployment Security
- ✅ Monitor access logs
- ✅ Set up alerts for failed authentication
- ✅ Regular security scans
- ✅ Database connection encryption
- ✅ API rate limiting (via Azure API Management)

---

## 📊 Monitoring & Logging

### Azure Application Insights
```python
# app/config.py
import logging
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

# Application Insights integration
if AZURE_INSIGHTS_CONNECTION_STRING:
    logging.getLogger().addHandler(
        AzureMonitorLogExporter(
            connection_string=AZURE_INSIGHTS_CONNECTION_STRING
        )
    )
```

### Health Check Monitoring
```bash
# Setup Azure Monitor alerts for:
GET /health  # Should return 200 OK
GET /       # Should return API info

# Database connectivity check
# External service availability
```

### Log Analysis Queries
```kusto
// Application Insights KQL queries
requests
| where timestamp > ago(24h)
| summarize count() by resultCode
| render piechart

exceptions
| where timestamp > ago(7d)
| summarize count() by problemId
| order by count_ desc
```

---

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow (Complete)
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run tests
        run: |
          python -m pytest tests/ -v --tb=short
        env:
          DATABASE_URL: sqlite:///./test.db
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Azure App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: 'Warung-Warga-api'
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
          package: .
```

---

## 🗄️ Database Migration

### Production Database Setup
```sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create profiles table
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_user_id UUID UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    location GEOGRAPHY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create listings table
-- (Full schema in app/models/lapak.py)

-- Create group_buys table
-- (Full schema in app/models/borongan.py)

-- Create group_buy_participants table
-- (Full schema in app/models/borongan.py)
```

### Migration Commands
```bash
# Alembic migration (if using)
alembic upgrade head

# Manual SQL execution via Supabase dashboard
# Or via psql connection
```

---

## 🔧 Performance Optimization

### Database Optimization
```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)
```

### Caching Strategy
```python
# Redis caching untuk production
from redis import Redis
import json

redis_client = Redis.from_url(REDIS_URL)

def cache_nearby_lapak(lat: float, lon: float, radius: int, data: dict):
    cache_key = f"nearby:{lat}:{lon}:{radius}"
    redis_client.setex(cache_key, 300, json.dumps(data))  # 5 min cache
```

### CDN Configuration
```bash
# Azure CDN untuk static assets
# Configure Azure Blob Storage dengan CDN endpoint
# Cache policy: 1 hour untuk images, 1 day untuk static files
```

---

## 🧪 Testing in Production

### Smoke Tests
```bash
# Production health check
curl https://api.warungwarga.com/health

# Authentication test
curl -X POST https://api.warungwarga.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'

# Protected endpoint test
curl -H "Authorization: Bearer $TOKEN" \
  https://api.warungwarga.com/users/users/me
```

### Load Testing
```bash
# Apache Bench
ab -n 1000 -c 10 https://api.warungwarga.com/health

# Artillery.js
artillery run load-test.yml
```

---

## 📞 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check Supabase connection
psql "postgresql://postgres:password@host:5432/database"

# Verify connection string in environment
echo $DATABASE_URL
```

#### 2. Azure Blob Storage Issues
```bash
# Test Azure connection
from azure.storage.blob import BlobServiceClient
client = BlobServiceClient.from_connection_string(connection_string)
client.list_containers()
```

#### 3. CORS Errors
```python
# Update CORS origins in app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Payment Webhook Not Working
```bash
# Ensure webhook URL is publicly accessible
# Check Tripay webhook logs in dashboard
# Verify HMAC signature validation
```

### Support Contacts
- **Azure Support**: Azure Portal > Support
- **Supabase Support**: support@supabase.io
- **Tripay Support**: support@tripay.co.id

---

## 📈 Scaling Considerations

### Auto-Scaling Rules
```bash
# Azure App Service scaling rules
az monitor autoscale create \
  --resource-group Warung-Warga-rg \
  --resource Warung-Warga-api \
  --min-count 1 \
  --max-count 10 \
  --count 2
```

### Database Scaling
- Supabase Pro plan untuk production
- Read replicas untuk heavy read workloads
- Connection pooling optimization

### Future Enhancements
- ✅ Redis caching layer
- ✅ Message queue (Azure Service Bus)
- ✅ Microservices architecture
- ✅ API versioning
- ✅ GraphQL endpoints

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificate configured
- [ ] Domain DNS configured
- [ ] External services tested
- [ ] Security review completed

### Deployment
- [ ] Code deployed via CI/CD
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Monitoring configured
- [ ] Backup strategy implemented

### Post-Deployment
- [ ] Smoke tests completed
- [ ] Load testing performed
- [ ] Error monitoring active
- [ ] Performance metrics baseline
- [ ] Team notification sent

---

**🎉 Deployment Complete! Warung Warga API is Production Ready! 🚀**

*Last Updated: January 2024* 