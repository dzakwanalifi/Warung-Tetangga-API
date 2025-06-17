# 🚀 Deployment Guide - Warung Tetangga API

**Production-Ready FastAPI Backend untuk Hyperlocal Marketplace**  
**🔥 Azure Functions Serverless Architecture**

🌐 **Production URL**: `https://api-warungtetangga.azurewebsites.net` ✅ **LIVE**  
📚 **API Documentation**: `https://api-warungtetangga.azurewebsites.net/docs` ✅ **OpenAPI FIXED**

## 📋 Prerequisites

### Required Services & Accounts
- ✅ **GitHub Account** (untuk repository)
- ✅ **Azure Account** (untuk hosting & blob storage)
- ✅ **Supabase Account** (untuk database & auth)
- ✅ **Tripay Account** (untuk payment gateway)
- ✅ **Google Cloud** (untuk Gemini AI)

### Required Tools
- Azure CLI (`az`)
- Azure Functions Core Tools (`func`)
- Python 3.11+
- Git

### Domain Requirements
- Production domain: `api-warungtetangga.azurewebsites.net`
- SSL certificate (auto-provisioned via Azure)
- **✅ OpenAPI Documentation**: Fixed and working at `/docs` and `/openapi.json`

---

## 🏗️ Infrastructure Architecture

```
Frontend (Vercel/Netlify)
    ↓ HTTPS API Calls
Backend API (Azure Functions - api-warungtetangga.azurewebsites.net)
    ↓ Database Queries
PostgreSQL (Supabase)
    ↓ File Storage
Azure Blob Storage (stwarungtetangga.blob.core.windows.net)
    ↓ External Services
[Tripay] [Google Gemini] [Supabase Auth]
```

**Production Project Structure:**
```
warung-tetangga-api/
├── api/                    # Azure Functions folder
│   ├── app/               # FastAPI application
│   │   └── main.py        # ✅ Fixed root_path & OpenAPI config
│   ├── function.json      # Function configuration
│   └── __init__.py        # ✅ Fixed ASGI path mapping
├── host.json              # Function app settings
├── requirements.txt       # Dependencies with azure-functions
├── .funcignore           # Files to ignore in deployment
├── local.settings.json   # Local development settings
└── .github/
    └── workflows/
        └── azure-functions-deploy.yml  # CI/CD pipeline
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
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=stwarungtetangga;AccountKey=...
AZURE_STORAGE_CONTAINER_NAME=lapak-images
```

### 3. Payment Gateway (Tripay)
```bash
# Tripay Configuration
TRIPAY_API_KEY=your-api-key
TRIPAY_PRIVATE_KEY=your-private-key
TRIPAY_MERCHANT_CODE=your-merchant-code
TRIPAY_MODE=production  # or 'sandbox' for testing
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

# CORS Settings (configured in FastAPI app)
ALLOWED_ORIGINS=["https://yourdomain.com", "http://localhost:3000"]
```

---

## ☁️ Primary Deployment: Azure Functions

### 🎯 Why Azure Functions?
- ✅ **Serverless** - No server management
- ✅ **Auto-scaling** - Handles traffic spikes automatically
- ✅ **Cost-effective** - Pay only for actual usage ($0 for low traffic)
- ✅ **Built-in monitoring** - Application Insights included
- ✅ **Easy CI/CD** - GitHub Actions integration
- ✅ **Production Ready** - Currently serving at `api-warungtetangga.azurewebsites.net`

### Step 1: Setup Azure Function App

#### Create Function App via Azure CLI
```bash
# Login to Azure
az login

# Create Resource Group
az group create --name warung-tetangga-rg --location "Southeast Asia"

# Create Storage Account (required for Functions)
az storage account create \
  --name stwarungtetangga \
  --resource-group warung-tetangga-rg \
  --location "Southeast Asia" \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group warung-tetangga-rg \
  --consumption-plan-location "Southeast Asia" \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name api-warungtetangga \
  --storage-account stwarungtetangga
```

### Step 2: Configure Environment Variables

#### Via Azure CLI
```bash
az functionapp config appsettings set \
  --name api-warungtetangga \
  --resource-group warung-tetangga-rg \
  --settings \
    "DATABASE_URL=your-supabase-connection-string" \
    "SUPABASE_URL=https://your-project.supabase.co" \
    "SUPABASE_ANON_KEY=your-anon-key" \
    "SUPABASE_SERVICE_ROLE_KEY=your-service-role-key" \
    "AZURE_STORAGE_CONNECTION_STRING=your-azure-storage-connection" \
    "AZURE_STORAGE_CONTAINER_NAME=lapak-images" \
    "TRIPAY_API_KEY=your-tripay-api-key" \
    "TRIPAY_PRIVATE_KEY=your-tripay-private-key" \
    "TRIPAY_MERCHANT_CODE=your-merchant-code" \
    "TRIPAY_MODE=production" \
    "GOOGLE_AI_API_KEY=your-gemini-api-key" \
    "SECRET_KEY=your-super-secret-key-min-32-chars" \
    "ALGORITHM=HS256" \
    "ACCESS_TOKEN_EXPIRE_MINUTES=30"
```

### Step 3: Deploy via Azure Functions Core Tools

#### Local Development Setup
```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Clone repository
git clone https://github.com/your-username/warung-tetangga-api.git
cd warung-tetangga-api

# Install dependencies
pip install -r requirements.txt

# Initialize local settings
func azure functionapp fetch-app-settings api-warungtetangga

# Local development (will run on http://localhost:7071)
func start
```

#### Deploy to Azure
```bash
# Deploy function app
func azure functionapp publish api-warungtetangga --python

# Verify deployment
curl https://api-warungtetangga.azurewebsites.net/health
```

### Step 4: GitHub Actions CI/CD (Automated Deployment)

The repository includes `.github/workflows/azure-functions-deploy.yml` for automated deployment:

#### Setup GitHub Secrets
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add these secrets:
   ```
   AZURE_FUNCTIONAPP_PUBLISH_PROFILE
   ```

#### Get Publish Profile
```bash
# Download publish profile
az functionapp deployment list-publishing-profiles \
  --name api-warungtetangga \
  --resource-group warung-tetangga-rg \
  --xml
```

Copy the XML content and paste it as the `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` secret.

### Step 5: Production Verification

#### Health Check
```bash
# Basic health check
curl https://api-warungtetangga.azurewebsites.net/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00Z",
#   "database": "connected",
#   "azure_functions": {
#     "environment": "production",
#     "region": "Southeast Asia",
#     "openapi_status": "working"
#   },
#   "documentation": {
#     "swagger_ui": "https://api-warungtetangga.azurewebsites.net/docs",
#     "openapi_json": "https://api-warungtetangga.azurewebsites.net/openapi.json",
#     "status": "operational"
#   }
# }
```

#### API Documentation Verification ✅
```bash
# Verify Swagger UI is accessible
curl -I https://api-warungtetangga.azurewebsites.net/docs
# Expected: HTTP/200 OK

# Verify OpenAPI JSON specification is available
curl https://api-warungtetangga.azurewebsites.net/openapi.json
# Expected: Complete OpenAPI 3.0 JSON schema

# Test interactive documentation
# Visit https://api-warungtetangga.azurewebsites.net/docs in browser
# Should show working Swagger UI with all endpoints
```

#### API Documentation URLs ✅
- **Interactive Docs**: https://api-warungtetangga.azurewebsites.net/docs ✅ **OpenAPI Working**
- **OpenAPI Spec**: https://api-warungtetangga.azurewebsites.net/openapi.json ✅ **Available**
- **API Reference**: https://api-warungtetangga.azurewebsites.net/redoc ✅ **ReDoc UI**

#### Test Endpoints
```bash
# Test welcome endpoint
curl https://api-warungtetangga.azurewebsites.net/

# Expected response includes documentation_status: "OpenAPI Fixed & Working"

# Test user registration
curl -X POST https://api-warungtetangga.azurewebsites.net/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","full_name":"Test User"}'
```

---

## 📊 Monitoring & Analytics

### Azure Application Insights
- **Monitoring**: Automatic performance tracking
- **Logs**: Real-time error monitoring
- **Metrics**: Request count, response time, error rate
- **Dashboard**: https://portal.azure.com (search for api-warungtetangga)
- **API Docs Access**: Monitor `/docs` and `/openapi.json` endpoint usage

### Key Metrics to Monitor
- **Response Time**: < 500ms (warm start)
- **Cold Start**: < 3 seconds
- **Error Rate**: < 1%
- **Availability**: > 99.9%
- **Documentation Access**: API docs load time < 1 second

### 🔧 OpenAPI-Specific Monitoring
- **Documentation Requests**: Monitor `/docs` endpoint access
- **Specification Downloads**: Track `/openapi.json` usage
- **Client Generation**: Usage patterns for API client generation
- **Developer Adoption**: API docs interaction metrics

---

## 🔒 Security Checklist

### Pre-Deployment Security
- ✅ Environment variables stored securely (Azure Key Vault recommended)
- ✅ API rate limiting configured
- ✅ CORS properly configured
- ✅ HTTPS enforced (automatic in Azure Functions)
- ✅ Authentication tokens with proper expiration
- ✅ Database connection encrypted
- ✅ File upload validation and size limits
- ✅ **API Documentation**: Public access secured for developer usage

### Post-Deployment Security
- ✅ Monitor API access logs
- ✅ Set up alerts for unusual traffic patterns
- ✅ Regular security updates
- ✅ Backup database regularly
- ✅ Review and rotate API keys quarterly
- ✅ **Monitor documentation access** untuk security analysis

---

## 🚦 Alternative Deployment Options

### Option 2: Azure App Service
For consistent traffic and specific scaling requirements:

```bash
# Create App Service Plan
az appservice plan create \
  --name warung-tetangga-plan \
  --resource-group warung-tetangga-rg \
  --location "Southeast Asia" \
  --sku B1

# Create Web App
az webapp create \
  --resource-group warung-tetangga-rg \
  --plan warung-tetangga-plan \
  --name warung-tetangga-api \
  --runtime "PYTHON|3.11"
```

### Option 3: Docker Container
For custom environments:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🎯 Production Optimization

### Performance Tips
1. **Cold Start Optimization**:
   - Keep dependencies minimal
   - Use connection pooling
   - Implement proper caching

2. **Cost Optimization**:
   - Monitor usage in Azure portal
   - Use consumption plan for variable traffic
   - Optimize database queries

3. **Scaling Strategy**:
   - Azure Functions auto-scales
   - Database: Consider read replicas for high traffic
   - Storage: Use CDN for static assets

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Function App Not Starting
```bash
# Check logs
func azure functionapp logstream api-warungtetangga

# Check configuration
az functionapp config show --name api-warungtetangga --resource-group warung-tetangga-rg
```

#### 2. Database Connection Issues
```bash
# Test connection string
python -c "
import psycopg2
conn = psycopg2.connect('your-database-url')
print('Database connected successfully')
"
```

#### 3. ✅ RESOLVED: OpenAPI Documentation Issues
**Previous Issue**: `/docs` and `/openapi.json` endpoints returning "Not Found"  
**Solution Applied**:
- ✅ Fixed Azure Functions handler untuk proper path extraction
- ✅ Updated FastAPI app configuration dengan correct `root_path`
- ✅ Configured ASGI scope untuk proper documentation endpoints

**Current Status**: ✅ **FULLY WORKING**

```bash
# Verify documentation is working
curl -I https://api-warungtetangga.azurewebsites.net/docs
curl https://api-warungtetangga.azurewebsites.net/openapi.json
```

#### 4. CORS Issues
Ensure allowed origins are configured in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Support Channels
- **Technical Issues**: dzakwanalifi@apps.ipb.ac.id
- **Azure Support**: Azure Portal → Support
- **Database Issues**: Supabase Dashboard → Support
- **API Documentation**: Working at https://api-warungtetangga.azurewebsites.net/docs

---

## 📈 Roadmap

### Phase 1: MVP (Current) ✅
- ✅ Basic API endpoints
- ✅ Authentication & user management
- ✅ Product listings with geo-search
- ✅ Group buying functionality
- ✅ Payment integration
- ✅ Azure Functions deployment
- ✅ **OpenAPI Documentation Fixed & Working**

### Phase 2: Enhancement
- [ ] Advanced search and filtering
- [ ] Real-time notifications
- [ ] Analytics dashboard
- [ ] Mobile app APIs
- [ ] Admin panel APIs
- [ ] **Enhanced API documentation** with examples & tutorials

### Phase 3: Scale
- [ ] Microservices architecture
- [ ] Advanced caching strategies
- [ ] Multi-region deployment
- [ ] Advanced monitoring and alerting
- [ ] **API versioning** dengan backward compatibility

---

**🚀 Deployment Guide Complete!**

*Production URL: https://api-warungtetangga.azurewebsites.net*  
*Interactive Documentation: https://api-warungtetangga.azurewebsites.net/docs ✅ OpenAPI Fixed*  
*OpenAPI Specification: https://api-warungtetangga.azurewebsites.net/openapi.json ✅ Working*  
*For technical support: dzakwanalifi@apps.ipb.ac.id*  
*Last Updated: January 2024 - OpenAPI Documentation Fixed*