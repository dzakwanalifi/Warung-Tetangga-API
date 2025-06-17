# Warung Tetangga API

## 🏪 Hyperlocal Marketplace Backend

**Warung Tetangga** is a hyperlocal marketplace API that enables neighborhood-based trading through two main features:
- **Lapak Warga**: Local product listings with geo-location
- **Borongan Bareng**: Group buying sessions with payment integration

Built with **FastAPI**, **PostgreSQL**, **Azure Cloud Services**, and **AI-powered features**.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL database (we recommend [Supabase](https://supabase.com) for easy setup)
- Azure Storage Account (for image uploads)
- Gemini AI API Key (for product analysis)
- Tripay Account (for payment processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd warung-tetangga-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

---

## 🔧 Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration - Supabase PostgreSQL
DATABASE_URL="postgresql://username:password@host:port/database"

# Supabase Configuration
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-supabase-anon-key"

# Security Configuration
SECRET_KEY="your-super-secret-key-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
AZURE_STORAGE_CONTAINER_NAME="lapak-images"

# Gemini AI Configuration
GEMINI_API_KEY="your-gemini-api-key"

# Tripay Payment Gateway (Sandbox)
TRIPAY_API_URL="https://tripay.co.id/api-sandbox"
TRIPAY_MERCHANT_CODE="your-merchant-code"
TRIPAY_API_KEY="your-tripay-api-key"
TRIPAY_PRIVATE_KEY="your-tripay-private-key"
```

---

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration with Supabase
- `POST /auth/login` - User authentication

### User Management
- `GET /users/users/me` - Get current user profile
- `PUT /users/users/me` - Update user profile

### Lapak Warga (Local Marketplace)
- `POST /lapak/analyze` - AI-powered product analysis from image
- `POST /lapak` - Create new product listing
- `GET /lapak/nearby` - Find nearby products (geo-spatial query)
- `GET /lapak/{listing_id}` - Get product details
- `PUT /lapak/{listing_id}` - Update product listing

### Borongan Bareng (Group Buying)
- `GET /borongan/` - List active group buying sessions
- `POST /borongan/` - Create new group buying session
- `GET /borongan/{borongan_id}` - Get group buying details
- `POST /borongan/{group_buy_id}/join` - Join group buying with payment

### Payment Integration
- `POST /payments/tripay/webhook` - Handle payment notifications
- `GET /payments/tripay/status/{participant_id}` - Check payment status
- `GET /payments/methods` - Get available payment methods

### System
- `GET /` - API welcome message
- `GET /health` - Health check endpoint

**Interactive API Documentation**: Visit `http://localhost:8000/docs` when running locally.

---

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI with Python 3.10+
- **Database**: PostgreSQL with PostGIS (via Supabase)
- **Authentication**: Supabase Auth with JWT
- **File Storage**: Azure Blob Storage
- **AI Integration**: Google Gemini AI
- **Payment Gateway**: Tripay
- **Testing**: pytest with SQLite in-memory

### Key Features
- **Geo-spatial Queries**: Find nearby products using PostGIS
- **AI-Powered Analysis**: Automatic product description from images
- **Real Payment Processing**: Complete payment flow with webhooks
- **Background Tasks**: Automated deadline processing
- **Comprehensive Testing**: 31+ passing tests
- **API Documentation**: Auto-generated with FastAPI

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_borongan.py -v

# Run with coverage
pytest --cov=app tests/
```

### Test Coverage
- ✅ **Authentication & User Management**: Complete CRUD operations
- ✅ **Lapak Warga**: Product listings with geo-location
- ✅ **Borongan Bareng**: Group buying with payment integration
- ✅ **Payment Processing**: Webhook handling and status tracking
- ✅ **AI Integration**: Image analysis with fallback

---

## 🚢 Deployment

### Azure Functions (Recommended)

1. **Install Azure CLI**
   ```bash
   # Install Azure CLI and Azure Functions Core Tools
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Create Azure Function App**
   ```bash
   func init --python
   func new --name warung-tetangga-api --template "HTTP trigger"
   ```

3. **Deploy to Azure**
   ```bash
   func azure functionapp publish <your-function-app-name>
   ```

### Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and run**
   ```bash
   docker build -t warung-tetangga-api .
   docker run -p 8000:8000 warung-tetangga-api
   ```

### Environment Variables for Production

Make sure to set all environment variables in your production environment:
- Use **production database credentials**
- Set **Tripay production API** instead of sandbox
- Use **strong SECRET_KEY**
- Configure **proper CORS origins**

---

## 🔒 Security Considerations

- ✅ **Environment Variables**: All secrets in `.env` (never commit!)
- ✅ **JWT Authentication**: Secure token-based auth with Supabase
- ✅ **CORS Configuration**: Properly configured for frontend domains
- ✅ **Input Validation**: Comprehensive Pydantic schemas
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM protection
- ✅ **Webhook Signature Validation**: HMAC-SHA256 for Tripay
- ✅ **File Upload Validation**: Content type and size checks

---

## 📈 Development Status

### ✅ Completed Features (MVP Ready)
- **Phase 1**: User authentication and profile management
- **Phase 2**: Lapak Warga with AI integration
- **Phase 3**: Borongan Bareng with payment processing
- **Testing**: Comprehensive test suite with 31+ passing tests
- **Documentation**: Complete API documentation

### 🔄 Next Steps
- Frontend development (Next.js)
- Advanced notifications system
- Performance optimization
- Production deployment

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

For questions and support:
- **Email**: admin@warungtetangga.com
- **Documentation**: Visit `/docs` endpoint for interactive API docs
- **Issues**: Open an issue on GitHub

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🏆 Acknowledgments

- **Supabase** for amazing PostgreSQL hosting
- **Azure** for reliable cloud storage
- **Google Gemini** for AI-powered features
- **Tripay** for seamless payment processing
- **FastAPI** for the incredible framework

**Made with ❤️ for Indonesian local communities** 