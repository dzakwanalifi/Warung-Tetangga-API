# 📚 API Documentation - Warung Warga

**Comprehensive API Reference untuk Hyperlocal Marketplace Platform**

Version: 1.0.0 | Last Updated: January 2024

---

## 🌐 Base Information

- **Base URL**: `https://api.warungwarga.com` (Production)
- **Base URL**: `http://localhost:8000` (Development)
- **API Version**: v1
- **Authentication**: Bearer Token (JWT)
- **Content Type**: `application/json`
- **Documentation**: Available at `/docs` (Swagger UI)

---

## 🔐 Authentication

### Bearer Token Format
```
Authorization: Bearer <jwt_token>
```

### Token Lifetime
- **Access Token**: 30 minutes
- **Refresh**: Handled via Supabase Auth

---

## 📊 Response Format

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "detail": "Error description",
  "status_code": 400
}
```

---

## 🔗 API Endpoints Overview

| Module | Endpoints | Authentication | Description |
|--------|-----------|----------------|-------------|
| **System** | 2 endpoints | ❌ Public | Health check & info |
| **Auth** | 2 endpoints | ❌ Public | Registration & login |
| **Users** | 2 endpoints | ✅ Required | Profile management |
| **Lapak** | 5 endpoints | ✅ Required | Product listings |
| **Borongan** | 4 endpoints | ✅ Required | Group buying |
| **Payments** | 3 endpoints | ✅ Required | Payment processing |

**Total: 18 endpoints**

---

## 🏠 System Endpoints

### 1. Welcome Message
```http
GET /
```

**Description**: Get API welcome message and version info

**Authentication**: ❌ Not required

**Response**:
```json
{
  "message": "Welcome to Warung Warga API",
  "version": "1.0.0",
  "status": "Production Ready",
  "endpoints": {
    "docs": "/docs",
    "health": "/health"
  }
}
```

### 2. Health Check
```http
GET /health
```

**Description**: System health check for monitoring

**Authentication**: ❌ Not required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected",
  "external_services": {
    "supabase": "connected",
    "azure_blob": "connected",
    "tripay": "connected"
  }
}
```

---

## 🔐 Authentication Module

### 1. User Registration
```http
POST /auth/register
```

**Description**: Register new user with Supabase Auth

**Authentication**: ❌ Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "email_confirmed_at": null
  },
  "profile": {
    "id": "uuid-string",
    "full_name": "John Doe",
    "email": "user@example.com"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid email format or weak password
- `409 Conflict`: Email already registered

### 2. User Login
```http
POST /auth/login
```

**Description**: Login user with email and password

**Authentication**: ❌ Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "email_confirmed_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Account not confirmed

---

## 👤 User Management Module

### 1. Get Current User Profile
```http
GET /users/users/me
```

**Description**: Get current authenticated user's profile

**Authentication**: ✅ Required

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "supabase_user_id": "uuid-string",
  "full_name": "John Doe",
  "email": "user@example.com",
  "phone": "+628123456789",
  "address": "Jl. Kebon Jeruk No. 123, Jakarta",
  "latitude": -6.200000,
  "longitude": 106.816666,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 2. Update User Profile
```http
PUT /users/users/me
```

**Description**: Update current user's profile information

**Authentication**: ✅ Required

**Request Body**:
```json
{
  "full_name": "John Doe Updated",
  "phone": "+628123456789",
  "address": "Jl. Kebon Jeruk No. 456, Jakarta",
  "latitude": -6.200000,
  "longitude": 106.816666
}
```

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "full_name": "John Doe Updated",
  "email": "user@example.com",
  "phone": "+628123456789",
  "address": "Jl. Kebon Jeruk No. 456, Jakarta",
  "latitude": -6.200000,
  "longitude": 106.816666,
  "updated_at": "2024-01-15T11:00:00Z"
}
```

---

## 🏪 Lapak Warga Module

### 1. AI Image Analysis
```http
POST /lapak/analyze
```

**Description**: Analyze product image using Google Gemini AI

**Authentication**: ✅ Required

**Request**: Multipart form-data
```
file: [image file] (PNG, JPG, JPEG, max 5MB)
```

**Response** (200 OK):
```json
{
  "title": "Nasi Gudeg Jogja",
  "description": "Nasi gudeg khas Jogja dengan kuah santan gurih dan ayam kampung empuk. Dilengkapi sambal krecek dan telur pindang.",
  "suggested_price": 25000,
  "unit": "porsi",
  "category": "Makanan"
}
```

### 2. Create New Lapak
```http
POST /lapak
```

**Description**: Create new product listing (lapak)

**Authentication**: ✅ Required

**Request**: Multipart form-data
```
title: "Nasi Gudeg Jogja"
description: "Nasi gudeg khas Jogja..."
price: 25000
unit: "porsi"
stock_quantity: 10
files: [image1.jpg, image2.jpg] (max 5 files, 5MB each)
```

**Response** (201 Created):
```json
{
  "id": "uuid-string",
  "title": "Nasi Gudeg Jogja",
  "description": "Nasi gudeg khas Jogja...",
  "price": 25000,
  "unit": "porsi",
  "stock_quantity": 10,
  "status": "available",
  "images": [
    "https://storage.azure.com/lapak-images/uuid1.jpg",
    "https://storage.azure.com/lapak-images/uuid2.jpg"
  ],
  "seller": {
    "id": "uuid-string",
    "full_name": "John Doe",
    "phone": "+628123456789"
  },
  "latitude": -6.200000,
  "longitude": 106.816666,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 3. Get Nearby Lapak
```http
GET /lapak/nearby?latitude=-6.200000&longitude=106.816666&radius=5000
```

**Description**: Get product listings near specified location

**Authentication**: ✅ Required

**Query Parameters**:
- `latitude` (required): User's latitude
- `longitude` (required): User's longitude  
- `radius` (optional): Search radius in meters (default: 5000m)

**Response** (200 OK):
```json
{
  "lapak_list": [
    {
      "id": "uuid-string",
      "title": "Nasi Gudeg Jogja",
      "price": 25000,
      "unit": "porsi",
      "status": "available",
      "main_image": "https://storage.azure.com/lapak-images/uuid1.jpg",
      "seller": {
        "full_name": "John Doe",
        "phone": "+628123456789"
      },
      "distance_meters": 1250,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1,
  "search_radius_km": 5.0
}
```

### 4. Get Lapak Detail
```http
GET /lapak/{listing_id}
```

**Description**: Get detailed information of specific lapak

**Authentication**: ✅ Required

**Path Parameters**:
- `listing_id`: UUID of the lapak

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Nasi Gudeg Jogja",
  "description": "Nasi gudeg khas Jogja dengan kuah santan gurih...",
  "price": 25000,
  "unit": "porsi",
  "stock_quantity": 8,
  "status": "available",
  "images": [
    "https://storage.azure.com/lapak-images/uuid1.jpg",
    "https://storage.azure.com/lapak-images/uuid2.jpg"
  ],
  "seller": {
    "id": "uuid-string",
    "full_name": "John Doe",
    "email": "seller@example.com",
    "phone": "+628123456789",
    "address": "Jl. Kebon Jeruk No. 123"
  },
  "latitude": -6.200000,
  "longitude": 106.816666,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### 5. Update Lapak
```http
PUT /lapak/{listing_id}
```

**Description**: Update lapak information (owner only)

**Authentication**: ✅ Required (must be owner)

**Path Parameters**:
- `listing_id`: UUID of the lapak

**Request Body**:
```json
{
  "title": "Nasi Gudeg Jogja Premium",
  "description": "Updated description...",
  "price": 30000,
  "stock_quantity": 15,
  "status": "available"
}
```

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Nasi Gudeg Jogja Premium",
  "price": 30000,
  "stock_quantity": 15,
  "status": "available",
  "updated_at": "2024-01-15T13:00:00Z"
}
```

---

## 🤝 Borongan Bareng Module

### 1. List Active Borongan
```http
GET /borongan/
```

**Description**: Get list of all active group buying sessions

**Authentication**: ✅ Required

**Response** (200 OK):
```json
{
  "borongan_list": [
    {
      "id": "uuid-string",
      "title": "Beras Premium 25kg",
      "description": "Beras premium kualitas terbaik...",
      "price_per_unit": 150000,
      "unit": "karung",
      "target_quantity": 20,
      "current_quantity": 12,
      "deadline": "2024-01-20T23:59:59Z",
      "status": "active",
      "pickup_point_address": "Jl. Raya Bogor KM 25",
      "progress_percentage": 60,
      "remaining_slots": 8,
      "supplier": {
        "full_name": "Supplier Beras Jakarta",
        "phone": "+628123456789"
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1
}
```

### 2. Create New Borongan
```http
POST /borongan/
```

**Description**: Create new group buying session

**Authentication**: ✅ Required

**Request Body**:
```json
{
  "title": "Beras Premium 25kg",
  "description": "Beras premium kualitas terbaik untuk keluarga",
  "price_per_unit": 150000,
  "unit": "karung",
  "target_quantity": 20,
  "deadline": "2024-01-20T23:59:59Z",
  "pickup_point_address": "Jl. Raya Bogor KM 25, Jakarta Timur"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-string",
  "title": "Beras Premium 25kg",
  "description": "Beras premium kualitas terbaik untuk keluarga",
  "price_per_unit": 150000,
  "unit": "karung",
  "target_quantity": 20,
  "current_quantity": 0,
  "deadline": "2024-01-20T23:59:59Z",
  "status": "active",
  "pickup_point_address": "Jl. Raya Bogor KM 25, Jakarta Timur",
  "supplier_id": "uuid-string",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 3. Get Borongan Detail
```http
GET /borongan/{borongan_id}
```

**Description**: Get detailed borongan information with participants

**Authentication**: ✅ Required

**Path Parameters**:
- `borongan_id`: UUID of the borongan

**Response** (200 OK):
```json
{
  "id": "uuid-string",
  "title": "Beras Premium 25kg",
  "description": "Beras premium kualitas terbaik untuk keluarga",
  "price_per_unit": 150000,
  "unit": "karung",
  "target_quantity": 20,
  "current_quantity": 12,
  "deadline": "2024-01-20T23:59:59Z",
  "status": "active",
  "pickup_point_address": "Jl. Raya Bogor KM 25, Jakarta Timur",
  "progress_percentage": 60,
  "remaining_slots": 8,
  "supplier": {
    "id": "uuid-string",
    "full_name": "Supplier Beras Jakarta",
    "phone": "+628123456789",
    "email": "supplier@example.com"
  },
  "participants": [
    {
      "id": "uuid-string",
      "user": {
        "full_name": "Participant 1",
        "phone": "+628111111111"
      },
      "quantity": 2,
      "total_amount": 300000,
      "payment_status": "paid",
      "joined_at": "2024-01-15T11:00:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 4. Join Borongan
```http
POST /borongan/{group_buy_id}/join
```

**Description**: Join group buying session with payment

**Authentication**: ✅ Required

**Path Parameters**:
- `group_buy_id`: UUID of the borongan

**Request Body**:
```json
{
  "quantity": 2
}
```

**Response** (201 Created):
```json
{
  "participant_id": "uuid-string",
  "borongan_title": "Beras Premium 25kg",
  "quantity": 2,
  "unit_price": 150000,
  "total_amount": 300000,
  "payment_status": "pending",
  "payment_url": "https://tripay.co.id/checkout/T123456789",
  "payment_reference": "T123456789",
  "payment_instructions": {
    "qris": "Scan QR code untuk pembayaran",
    "virtual_account": "Transfer ke VA: 8001234567890123",
    "expiry_time": "2024-01-15T23:59:59Z"
  },
  "message": "Silakan lakukan pembayaran untuk mengkonfirmasi partisipasi"
}
```

---

## 💳 Payment Module

### 1. Tripay Webhook
```http
POST /payments/tripay/webhook
```

**Description**: Handle payment notifications from Tripay

**Authentication**: ❌ Not required (verified via signature)

**Headers**:
```
X-Callback-Signature: hmac-sha256-signature
```

**Request Body**:
```json
{
  "reference": "T123456789",
  "merchant_ref": "participant-uuid",
  "payment_method": "QRIS",
  "payment_method_code": "QRIS",
  "total_amount": 300000,
  "fee_merchant": 5000,
  "fee_customer": 0,
  "total_fee": 5000,
  "amount_received": 295000,
  "is_closed_payment": 1,
  "status": "PAID",
  "paid_at": 1642234567
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Payment processed successfully"
}
```

### 2. Check Payment Status
```http
GET /payments/tripay/status/{participant_id}
```

**Description**: Check payment status for specific participant

**Authentication**: ✅ Required

**Path Parameters**:
- `participant_id`: UUID of the participant

**Response** (200 OK):
```json
{
  "participant_id": "uuid-string",
  "payment_reference": "T123456789",
  "payment_status": "paid",
  "total_amount": 300000,
  "paid_at": "2024-01-15T14:30:00Z",
  "payment_method": "QRIS",
  "borongan": {
    "title": "Beras Premium 25kg",
    "quantity": 2
  }
}
```

### 3. Get Payment Methods
```http
GET /payments/methods
```

**Description**: Get available payment methods from Tripay

**Authentication**: ✅ Required

**Response** (200 OK):
```json
{
  "payment_methods": [
    {
      "code": "QRIS",
      "name": "QRIS",
      "type": "qr",
      "fee_merchant": {
        "flat": 0,
        "percent": 0.7
      },
      "fee_customer": {
        "flat": 0,
        "percent": 0
      },
      "minimum_fee": 0,
      "maximum_fee": 0,
      "is_active": true
    },
    {
      "code": "BRIVA",
      "name": "BRI Virtual Account",
      "type": "virtual_account",
      "fee_merchant": {
        "flat": 4000,
        "percent": 0
      },
      "is_active": true
    }
  ]
}
```

---

## 🔧 Background Tasks

### Deadline Check Trigger
```http
POST /borongan/internal/trigger-deadline-check
```

**Description**: Internal endpoint to trigger deadline checking (for cron jobs)

**Authentication**: ❌ Not required (internal use)

**Response** (200 OK):
```json
{
  "status": "completed",
  "processed_count": 3,
  "expired_borongan": [
    {
      "id": "uuid-string",
      "title": "Expired Borongan",
      "old_status": "active",
      "new_status": "failed"
    }
  ],
  "timestamp": "2024-01-15T15:00:00Z"
}
```

---

## 📝 Request Examples

### Using cURL

#### Login and Get Profile
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get profile (replace TOKEN with actual token)
curl -X GET http://localhost:8000/users/users/me \
  -H "Authorization: Bearer TOKEN"
```

#### Create Lapak with Images
```bash
curl -X POST http://localhost:8000/lapak \
  -H "Authorization: Bearer TOKEN" \
  -F "title=Nasi Gudeg" \
  -F "description=Nasi gudeg enak" \
  -F "price=25000" \
  -F "unit=porsi" \
  -F "stock_quantity=10" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg"
```

### Using JavaScript (Fetch)

#### Get Nearby Lapak
```javascript
const response = await fetch('/lapak/nearby?latitude=-6.2&longitude=106.8&radius=5000', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
```

#### Join Borongan
```javascript
const response = await fetch(`/borongan/${boronganId}/join`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ quantity: 2 })
});
const result = await response.json();
// Redirect to payment_url for payment
window.location.href = result.payment_url;
```

---

## ❌ Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Common Error Responses

#### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

#### Authentication Error (401)
```json
{
  "detail": "Could not validate credentials"
}
```

#### Permission Error (403)
```json
{
  "detail": "You don't have permission to access this resource"
}
```

---

## 🔄 Rate Limiting

| Endpoint Type | Rate Limit | Window |
|---------------|------------|---------|
| Authentication | 10 requests | 1 minute |
| File Upload | 5 requests | 1 minute |
| General API | 100 requests | 1 minute |
| Payment Webhook | Unlimited | - |

---

## 📱 Mobile App Integration

### Flutter/React Native Example
```dart
// Flutter HTTP request example
final response = await http.post(
  Uri.parse('${baseUrl}/auth/login'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'email': email,
    'password': password,
  }),
);

if (response.statusCode == 200) {
  final data = jsonDecode(response.body);
  final token = data['access_token'];
  // Store token securely
}
```

---

## 🧪 Testing

### Test Environment
- **Base URL**: `http://localhost:8000`
- **Test Database**: SQLite/Supabase Test Project
- **Payment**: Tripay Sandbox Mode

### Test Credentials
```
Email: test@warungwarga.com
Password: TestPassword123!
```

---

**📚 Documentation Complete! Ready for Development Team! 🚀**

*For technical support: team@warungwarga.com*  
*Last Updated: January 2024* 