# ADI Engineer Agent API Design

## Overview
This document outlines the API design for the ADI Engineer Agent, including endpoints, request/response formats, and authentication.

## Base URL
```
https://api.adi-engineer.com/v1
```

## Authentication

### 1. API Key Authentication
```http
Authorization: Bearer <api_key>
```

### 2. OAuth2 Authentication
```http
Authorization: Bearer <access_token>
```

## Endpoints

### 1. Product Search

#### Request
```http
GET /products/search
```

Query Parameters:
```json
{
  "query": "string",
  "application_area": "string",
  "parameters": [
    {
      "name": "string",
      "unit": "string",
      "min": number | string,
      "max": number | string
    }
  ],
  "features": ["string"],
  "page": number,
  "page_size": number
}
```

#### Response
```json
{
  "total": number,
  "page": number,
  "page_size": number,
  "products": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "parameters": {
        "name": {
          "value": number | string,
          "unit": "string",
          "min": number | string,
          "max": number | string
        }
      },
      "features": ["string"],
      "applications": ["string"],
      "datasheet_url": "string",
      "evaluation_board_url": "string"
    }
  ]
}
```

### 2. Solution Search

#### Request
```http
GET /solutions/search
```

Query Parameters:
```json
{
  "query": "string",
  "application_domain": "string",
  "requirements": [
    {
      "parameter": "string",
      "unit": "string",
      "min": number | string,
      "max": number | string
    }
  ],
  "format": "all" | "schematic" | "layout" | "code",
  "page": number,
  "page_size": number
}
```

#### Response
```json
{
  "total": number,
  "page": number,
  "page_size": number,
  "solutions": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "requirements": {
        "parameter": {
          "value": number | string,
          "unit": "string",
          "min": number | string,
          "max": number | string
        }
      },
      "reference_designs": [
        {
          "id": "string",
          "name": "string",
          "format": "string",
          "url": "string",
          "description": "string"
        }
      ],
      "products": [
        {
          "id": "string",
          "name": "string",
          "role": "string"
        }
      ]
    }
  ]
}
```

### 3. Parameter Analysis

#### Request
```http
POST /parameters/analyze
```

Request Body:
```json
{
  "products": ["string"],
  "parameters": ["string"],
  "constraints": [
    {
      "parameter": "string",
      "unit": "string",
      "min": number | string,
      "max": number | string
    }
  ]
}
```

#### Response
```json
{
  "comparison": {
    "parameter": {
      "unit": "string",
      "values": {
        "product_id": {
          "min": number,
          "max": number,
          "value": number
        }
      }
    }
  },
  "validation": {
    "product_id": {
      "parameter": {
        "status": "valid" | "invalid",
        "message": "string"
      }
    }
  },
  "compatibility": {
    "product_id": {
      "status": "compatible" | "incompatible",
      "message": "string"
    }
  }
}
```

### 4. Reference Design Download

#### Request
```http
GET /reference-designs/{design_id}/files/{file_id}
```

#### Response
```http
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="design.pdf"
```

### 5. Health Check

#### Request
```http
GET /health
```

#### Response
```json
{
  "status": "healthy" | "degraded" | "unhealthy",
  "version": "string",
  "timestamp": "string",
  "services": {
    "database": "healthy" | "degraded" | "unhealthy",
    "cache": "healthy" | "degraded" | "unhealthy",
    "api": "healthy" | "degraded" | "unhealthy"
  }
}
```

## Error Handling

### 1. Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": object
  }
}
```

### 2. Error Codes
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error
- `503`: Service Unavailable

### 3. Rate Limiting
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1623456789
```

## API Versioning

### 1. URL Versioning
```
https://api.adi-engineer.com/v1/products
https://api.adi-engineer.com/v2/products
```

### 2. Header Versioning
```http
Accept: application/vnd.adi-engineer.v1+json
```

## Caching

### 1. Cache-Control Headers
```http
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

### 2. Conditional Requests
```http
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
If-Modified-Since: Wed, 21 Oct 2015 07:28:00 GMT
```

## Webhooks

### 1. Webhook Registration

#### Request
```http
POST /webhooks
```

Request Body:
```json
{
  "url": "string",
  "events": ["product.update", "solution.update"],
  "secret": "string"
}
```

#### Response
```json
{
  "id": "string",
  "url": "string",
  "events": ["string"],
  "status": "active" | "inactive",
  "created_at": "string"
}
```

### 2. Webhook Events
```json
{
  "event": "product.update",
  "timestamp": "string",
  "data": {
    "id": "string",
    "name": "string",
    "changes": {
      "field": "old_value" | "new_value"
    }
  }
}
```

## SDK Examples

### 1. Python SDK
```python
from adi_engineer import ADIEngineerClient

client = ADIEngineerClient(api_key="your_api_key")

# Search for products
products = client.search_products(
    query="amplifier",
    application_area="sensor interface",
    parameters=[
        {
            "name": "supply_voltage",
            "unit": "V",
            "min": 3.0,
            "max": 3.6
        }
    ]
)

# Analyze parameters
analysis = client.analyze_parameters(
    products=["AD8232", "AD8422"],
    parameters=["supply_voltage", "gain"],
    constraints=[
        {
            "parameter": "supply_voltage",
            "unit": "V",
            "min": 3.0,
            "max": 3.6
        }
    ]
)
```

### 2. JavaScript SDK
```javascript
const { ADIEngineerClient } = require('@adi/engineer');

const client = new ADIEngineerClient({
  apiKey: 'your_api_key'
});

// Search for solutions
const solutions = await client.searchSolutions({
  query: 'temperature measurement',
  applicationDomain: 'industrial',
  requirements: [
    {
      parameter: 'temperature_range',
      unit: '°C',
      min: -40,
      max: 85
    }
  ]
});

// Download reference design
const file = await client.downloadReferenceDesign(
  'CN0428',
  'CN0428-SCH'
);
```

## API Documentation

### 1. OpenAPI Specification
```yaml
openapi: 3.0.0
info:
  title: ADI Engineer Agent API
  version: 1.0.0
  description: API for the ADI Engineer Agent
servers:
  - url: https://api.adi-engineer.com/v1
    description: Production server
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: Authorization
    OAuth2Auth:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: /oauth/token
          scopes: {}
paths:
  /products/search:
    get:
      summary: Search for products
      parameters:
        - name: query
          in: query
          schema:
            type: string
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProductSearchResponse'
```

### 2. API Reference
The complete API reference is available at:
```
https://api.adi-engineer.com/docs
```

## Conclusion
This API design provides:
- Clear and consistent endpoints
- Comprehensive error handling
- Proper versioning support
- Efficient caching mechanisms
- Webhook integration
- SDK support for multiple languages

The design follows RESTful principles and industry best practices to ensure a robust and maintainable API. 