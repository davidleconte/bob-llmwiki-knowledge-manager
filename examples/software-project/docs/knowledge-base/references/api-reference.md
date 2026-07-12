# REST API Reference

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.example.com`

## Authentication
All endpoints require JWT authentication except `/auth/login` and `/auth/register`.

```bash
# Include token in Authorization header
Authorization: Bearer <jwt_token>
```

## User Service (Port 8001)

### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-07-11T10:00:00Z"
}
```

### POST /auth/login
Authenticate and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Product Service (Port 8002)

### GET /products
List all products with pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `category` (string): Filter by category

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Product Name",
      "price": 29.99,
      "category": "electronics",
      "stock": 100
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

### GET /products/{id}
Get product details by ID.

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Product Name",
  "description": "Product description",
  "price": 29.99,
  "category": "electronics",
  "stock": 100,
  "images": ["url1", "url2"]
}
```

## Order Service (Port 8003)

### POST /orders
Create a new order.

**Request:**
```json
{
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2
    }
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "City",
    "country": "Country",
    "postal_code": "12345"
  }
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "status": "pending",
  "total": 59.98,
  "created_at": "2026-07-11T10:00:00Z"
}
```

### GET /orders/{id}
Get order details by ID.

**Response (200):**
```json
{
  "id": "uuid",
  "status": "completed",
  "items": [...],
  "total": 59.98,
  "created_at": "2026-07-11T10:00:00Z",
  "updated_at": "2026-07-11T10:30:00Z"
}
```

## Error Responses

All endpoints may return these error codes:

**400 Bad Request:**
```json
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": {...}
}
```

**401 Unauthorized:**
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

**404 Not Found:**
```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting
- 100 requests per minute per IP
- 1000 requests per hour per user

## Related Documents
- [Setup Guide](../guides/setup-guide.md)
- [Microservices Architecture](../concepts/microservices.md)
