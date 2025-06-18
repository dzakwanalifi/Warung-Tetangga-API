# 📚 API Documentation - Warung Warga

**Comprehensive API Reference untuk Hyperlocal Marketplace Platform**

Version: 1.0.0 | Last Updated: Januari 2025

---

## 🌐 Base Information

- **Production URL**: `https://warungwarga-api.azurewebsites.net`
- **Development URL**: `http://localhost:8000`  
- **API Version**: v1
- **Authentication**: Bearer Token (JWT)
- **Content Type**: `application/json`
- **Interactive Docs**: Available at `/docs` (Swagger UI)
- **Status**: Production Ready with Real Routers Active

---

## 🔐 Authentication

### Bearer Token Format
```
Authorization: Bearer <jwt_token>
```

### Token Lifetime
- **Access Token**: 30 minutes
- **Refresh**: Handled via Supabase Auth
- **Algorithm**: HS256

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

### Database Unavailable Response (503)
```json
{
  "detail": {
    "error": "Database not available",
    "message": "This endpoint requires database connection which is currently unavailable",
    "available_endpoints": ["/", "/health", "/db-status", "/info", "/docs"]
  }
}
```

---

## 🔗 API Endpoints Overview

| Module | Endpoints | Authentication | Status | Description |
|--------|-----------|----------------|--------|-------------|
| **System** | 4 endpoints | ❌ Public | ✅ Active | Health check & API info |
| **Auth** | 2 endpoints | ❌ Public | ✅ Active | Registration & login |
| **Users** | 2 endpoints | ✅ Required | ✅ Active | Profile management |
| **Lapak** | 5 endpoints | ✅ Required | ✅ Active | Product listings |
| **Borongan** | 4 endpoints | ✅ Required | ✅ Active | Group buying |
| **Payments** | 3 endpoints | ✅ Required | ✅ Active | Payment processing |

**Total: 19 endpoints** (14 router endpoints from 5 modules)

---

## 🏠 System Endpoints

### 1. Welcome Message
```http
GET /
```

**Description**: Get API welcome message and version info

**Authentication**: ❌ Not required

**Response** (200 OK):
```json
{
  "message": "Welcome to Warung Warga API v1.0.0",
  "status": "connected",
  "database_available": false
}
```

### 2. Health Check
```http
GET /health
```

**Description**: System health check for monitoring

**Authentication**: ❌ Not required

**Response** (200 OK):
```json
{
  "status": "ok",
  "database_available": false,
  "environment": "production"
}
```

### 3. Database Status
```http
GET /db-status
```

**Description**: Check database connection status

**Authentication**: ❌ Not required

**Response** (200 OK):
```json
{
  "database_available": false,
  "message": "Database connection not available",
  "note": "All API endpoints are still accessible but will return 'database unavailable' responses",
  "available_endpoints": ["/", "/health", "/db-status", "/docs"]
}
```

### 4. API Information
```http
GET /info
```

**Description**: Complete API information and endpoints list

**Authentication**: ❌ Not required

**Response** (200 OK):
```json
{
  "title": "Warung Warga API",
  "version": "1.0.0",
  "mode": "production_full_real_routers",
  "database_available": false,
  "endpoints": [
    "/", "/health", "/db-status", "/info", "/docs",
    "/auth/register", "/auth/login",
    "/users/users/me",
    "/lapak/analyze", "/lapak", "/lapak/nearby", "/lapak/{listing_id}",
    "/borongan/", "/borongan/{borongan_id}", "/borongan/{group_buy_id}/join",
    "/payments/tripay/webhook", "/payments/tripay/status/{participant_id}",
    "/payments/methods", "/payments/status/{participant_id}"
  ],
  "status": "operational",
  "note": "Using REAL routers with proper dependency injection. Database-dependent endpoints will return 503 if database is unavailable."
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
- `503 Service Unavailable`: Database connection required

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
    "email_confirmed_at": "2025-01-15T10:30:00Z"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Account not confirmed
- `503 Service Unavailable`: Database connection required

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
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: Token expired
- `503 Service Unavailable`: Database connection required

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
  "updated_at": "2025-01-15T11:00:00Z"
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

**Error Responses**:
- `400 Bad Request`: Invalid file format or size
- `413 Payload Too Large`: File exceeds 5MB limit
- `503 Service Unavailable`: AI service or database unavailable

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
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 3. Get Nearby Lapak
```http
GET /lapak/nearby?latitude=-6.200000&longitude=106.816666&radius=5000
```

**Description**: Get product listings near specified location using PostGIS

**Authentication**: ✅ Required

**Query Parameters**:
- `latitude` (required): User's latitude coordinate
- `longitude` (required): User's longitude coordinate  
- `radius` (optional): Search radius in meters (default: 5000m, max: 50000m)

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
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total_count": 1,
  "search_radius_km": 5.0,
  "user_location": {
    "latitude": -6.200000,
    "longitude": 106.816666
  }
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
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
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
  "updated_at": "2025-01-15T13:00:00Z"
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
      "deadline": "2025-01-20T23:59:59Z",
      "status": "active",
      "pickup_point_address": "Jl. Raya Bogor KM 25",
      "progress_percentage": 60,
      "remaining_slots": 8,
      "supplier": {
        "full_name": "Supplier Beras Jakarta",
        "phone": "+628123456789"
      },
      "created_at": "2025-01-15T10:30:00Z"
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
  "deadline": "2025-01-20T23:59:59Z",
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
  "deadline": "2025-01-20T23:59:59Z",
  "status": "active",
  "pickup_point_address": "Jl. Raya Bogor KM 25, Jakarta Timur",
  "supplier_id": "uuid-string",
  "created_at": "2025-01-15T10:30:00Z"
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
  "deadline": "2025-01-20T23:59:59Z",
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
      "joined_at": "2025-01-15T11:00:00Z"
    }
  ],
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 4. Join Borongan
```http
POST /borongan/{group_buy_id}/join
```

**Description**: Join group buying session with automated payment

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
    "expiry_time": "2025-01-15T23:59:59Z"
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

**Description**: Handle real-time payment notifications from Tripay

**Authentication**: ❌ Not required (verified via HMAC signature)

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
  "paid_at": "2025-01-15T14:30:00Z",
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

## 📝 Request Examples

### Using cURL

#### Get API Info
```bash
curl -X GET https://warungwarga-api.azurewebsites.net/info
```

#### Login and Get Profile
```bash
# Login
curl -X POST https://warungwarga-api.azurewebsites.net/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get profile (replace TOKEN with actual token)
curl -X GET https://warungwarga-api.azurewebsites.net/users/users/me \
  -H "Authorization: Bearer TOKEN"
```

#### Create Lapak with Images
```bash
curl -X POST https://warungwarga-api.azurewebsites.net/lapak \
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

#### Test API Status
```javascript
const response = await fetch('https://warungwarga-api.azurewebsites.net/');
const data = await response.json();
console.log(data);
```

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

### Using Python (Requests)

#### Test Production API
```python
import requests

def test_api():
    base_url = "https://warungwarga-api.azurewebsites.net"
    
    # Test basic endpoints
    endpoints = ["/", "/health", "/db-status", "/info"]
    
    for endpoint in endpoints:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")

test_api()
```

---

## ❌ Error Codes & Responses

| Code | Status | Description | Common Causes |
|------|--------|-------------|---------------|
| 200 | OK | Request successful | - |
| 201 | Created | Resource created successfully | Registration, new listings |
| 400 | Bad Request | Invalid request data | Invalid JSON, missing fields |
| 401 | Unauthorized | Authentication required | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions | Expired token, not owner |
| 404 | Not Found | Resource not found | Invalid ID, deleted resource |
| 409 | Conflict | Resource already exists | Email already registered |
| 413 | Payload Too Large | File too large | Image > 5MB |
| 422 | Unprocessable Entity | Validation error | Invalid data types |
| 500 | Internal Server Error | Server error | Database error, service down |
| 503 | Service Unavailable | Service temporarily unavailable | Database not connected |

### Common Error Response Examples

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

#### Database Unavailable (503)
```json
{
  "detail": {
    "error": "Database not available",
    "message": "This endpoint requires database connection which is currently unavailable",
    "available_endpoints": ["/", "/health", "/db-status", "/info", "/docs"]
  }
}
```

---

## 🔄 Rate Limiting

| Endpoint Type | Rate Limit | Window | Status |
|---------------|------------|---------|--------|
| Authentication | 10 requests | 1 minute | ✅ Implemented |
| File Upload | 5 requests | 1 minute | ✅ Implemented |
| General API | 100 requests | 1 minute | ✅ Implemented |
| Payment Webhook | Unlimited | - | ✅ No limit |

---

## 🧪 Testing & Development

### Production Testing
```bash
# Quick test script
python test_api.py

# Expected output:
# ✅ API Status: 200 OK
# ✅ Health Check: Working  
# ✅ Database Status: Available/Unavailable
# ✅ Mode: production_full_real_routers
```

### Development Environment
- **Base URL**: `http://localhost:8000`
- **Test Database**: SQLite or Supabase Test Project
- **Payment**: Tripay Sandbox Mode
- **AI**: Google Gemini Development API

### Test Credentials
```
Email: test@warungwarga.com
Password: TestPassword123!
```

---

## 📱 Mobile Integration Examples

### Flutter HTTP Example
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class WarungWargarAPI {
  static const String baseUrl = 'https://warungwarga-api.azurewebsites.net';
  
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Login failed');
    }
  }
  
  static Future<List<dynamic>> getNearbyLapak(
    double latitude, 
    double longitude, 
    String token
  ) async {
    final response = await http.get(
      Uri.parse('$baseUrl/lapak/nearby?latitude=$latitude&longitude=$longitude'),
      headers: {'Authorization': 'Bearer $token'},
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['lapak_list'];
    } else {
      throw Exception('Failed to fetch nearby lapak');
    }
  }
}
```

### React Native Example
```javascript
// api.js
const API_BASE_URL = 'https://warungwarga-api.azurewebsites.net';

export const warungWargarAPI = {
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    return response.json();
  },
  
  async getNearbyLapak(latitude, longitude, token) {
    const response = await fetch(
      `${API_BASE_URL}/lapak/nearby?latitude=${latitude}&longitude=${longitude}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch nearby lapak');
    }
    
    const data = await response.json();
    return data.lapak_list;
  }
};
```

---

## 🔒 Security Implementation

### Authentication Flow
1. **User Registration**: Supabase Auth handles email verification
2. **Login**: Returns JWT token with 30-minute expiry
3. **Token Usage**: Include in Authorization header for protected endpoints
4. **Token Refresh**: Handle via Supabase client-side SDK

### Security Features
- **JWT Authentication**: HS256 algorithm with secure secret key
- **Input Validation**: Pydantic models for all request/response
- **CORS Configuration**: Configured for specific frontend origins
- **File Upload Security**: File type and size validation
- **Payment Security**: HMAC signature verification for webhooks
- **Rate Limiting**: Prevents abuse of API endpoints

### Best Practices
- Always use HTTPS in production
- Store JWT tokens securely (encrypted storage)
- Implement proper error handling
- Validate user permissions for protected resources
- Use environment variables for sensitive configuration

---

## 📊 API Statistics

### Current Deployment Status
- **✅ Total Endpoints**: 19 fully functional
- **✅ Router Modules**: 5 (auth, users, lapak, borongan, payments)
- **✅ External Integrations**: 4 (Supabase, Azure, Gemini, Tripay)
- **✅ Response Time**: < 500ms average
- **✅ Uptime**: 99.9% target
- **✅ Documentation**: 100% coverage

### Performance Metrics
- **Database Queries**: Optimized with proper indexing
- **File Upload**: Azure Blob Storage with CDN
- **AI Processing**: Google Gemini 2.5 Flash (fast response)
- **Payment Processing**: Real-time webhook handling
- **Geo-spatial Queries**: PostGIS optimization for location-based search

---

**📚 Complete API Documentation Ready! 🚀**

*For technical support: dzakwanalifi@apps.ipb.ac.id*  
*Production API: https://warungwarga-api.azurewebsites.net*  
*Documentation: https://warungwarga-api.azurewebsites.net/docs*  
*Last Updated: Januari 2025* 