# REST API Design Principles

## What is REST?

REST (Representational State Transfer) is an architectural style for designing networked applications. It relies on standard HTTP methods to perform operations on resources.

## Core HTTP Methods

### GET
Retrieve data without modifying it. Safe and idempotent.

```
GET /api/users
GET /api/users/123
GET /api/users?role=admin&limit=10
```

### POST
Create a new resource. Not idempotent (repeated calls create multiple resources).

```
POST /api/users
Body: {"name": "John", "email": "john@example.com"}
Returns: 201 Created + Location header
```

### PUT
Replace an entire resource. Idempotent.

```
PUT /api/users/123
Body: {"name": "Jane", "email": "jane@example.com"}
Returns: 200 OK
```

### PATCH
Partially update a resource. May or may not be idempotent.

```
PATCH /api/users/123
Body: {"email": "newemail@example.com"}
Returns: 200 OK
```

### DELETE
Remove a resource. Idempotent.

```
DELETE /api/users/123
Returns: 204 No Content or 200 OK
```

## Status Codes

| Code | Meaning | When to Use |
|------|---------|-----------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Success, no response body |
| 400 | Bad Request | Client error (invalid data) |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Server error |

## Naming Conventions

### Use nouns for resources, not verbs

❌ Bad:
```
GET /api/getUsers
POST /api/createUser
DELETE /api/removeUser/123
```

✅ Good:
```
GET /api/users
POST /api/users
DELETE /api/users/123
```

### Use plural resource names consistently

```
GET /api/products
GET /api/products/42
GET /api/products/42/reviews
```

### Use lowercase and hyphens for multi-word resources

```
GET /api/user-profiles
GET /api/search-queries
```

## Request/Response Format

### Standard JSON Request

```
POST /api/products
Content-Type: application/json

{
  "name": "Laptop",
  "price": 999.99,
  "category": "Electronics"
}
```

### Standard JSON Response

```
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/products/789

{
  "id": 789,
  "name": "Laptop",
  "price": 999.99,
  "category": "Electronics",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Error Handling

Return consistent error responses:

```json
{
  "error": "Validation error",
  "status": 400,
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

## Pagination

For endpoints returning many items:

```
GET /api/users?page=2&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 156,
    "pages": 8
  }
}
```

## Versioning

Include API version in URL or header:

```
GET /api/v1/users
GET /api/v2/users  # Breaking changes in v2
```

Or via header:

```
GET /api/users
Header: Accept: application/vnd.api+json;version=2
```

## Authentication

### Basic Auth (not secure without HTTPS)
```
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

### Bearer Token (JWT)
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key
```
X-API-Key: your-api-key-here
```

## Best Practices

1. **Use HTTPS** - Always encrypt data in transit
2. **Rate limiting** - Prevent abuse
3. **Caching** - Use HTTP cache headers for performance
4. **Documentation** - Document your API endpoints clearly (OpenAPI/Swagger)
5. **Consistency** - Follow conventions across all endpoints
6. **Backwards compatibility** - Don't break existing clients

## Conclusion

Good REST API design improves usability, maintainability, and reduces bugs. Follow these principles to build APIs that developers love.
