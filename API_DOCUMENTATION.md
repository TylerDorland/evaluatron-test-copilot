# API Documentation

## Authentication

All API endpoints (except `/health` and authentication endpoints) require a JWT bearer token.

### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Register
```http
POST /api/auth/register
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "company_id": 1
}
```

## Companies

### List Companies
```http
GET /api/companies/
Authorization: Bearer <token>
```

### Get Company
```http
GET /api/companies/{company_id}
Authorization: Bearer <token>
```

### Create Company (Superuser only)
```http
POST /api/companies/
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "name": "New Company"
}
```

## Topics

### List Topics
```http
GET /api/topics/
Authorization: Bearer <token>
```

### Get Topic
```http
GET /api/topics/{topic_id}
Authorization: Bearer <token>
```

### Create Topic
```http
POST /api/topics/
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "name": "Customer Support",
  "description": "Customer support related queries",
  "company_id": 1
}
```

## LLM Queries

### Create Query
```http
POST /api/queries/
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "prompt": "What is the capital of France?",
  "llm_provider": "openai",
  "model_name": "gpt-3.5-turbo",
  "topic_id": 1
}
```

**Supported LLM Providers:**
- `openai` - OpenAI GPT models (default: gpt-3.5-turbo)
- `anthropic` - Anthropic Claude models (default: claude-3-sonnet-20240229)
- `google` - Google Gemini models (default: gemini-pro)

Response:
```json
{
  "id": 1,
  "prompt": "What is the capital of France?",
  "response": "The capital of France is Paris...",
  "llm_provider": "openai",
  "model_name": "gpt-3.5-turbo",
  "status": "completed",
  "tokens_used": 25,
  "latency_ms": 1234,
  "created_at": "2024-01-01T12:00:00Z",
  "topic_id": 1
}
```

### List Queries
```http
GET /api/queries/?skip=0&limit=100&topic_id=1
Authorization: Bearer <token>
```

### Get Query
```http
GET /api/queries/{query_id}
Authorization: Bearer <token>
```

## Evaluations

### Create Evaluation
```http
POST /api/evaluations/
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "llm_query_id": 1,
  "evaluation_type": "sentiment"
}
```

**Supported Evaluation Types:**
- `sentiment` - Sentiment analysis (-1 to 1, negative to positive)
- `clarity` - Readability and clarity (0 to 1)
- `accuracy` - Accuracy based on heuristics or keywords (0 to 1)

Response:
```json
{
  "id": 1,
  "llm_query_id": 1,
  "evaluation_type": "sentiment",
  "score": 0.85,
  "details": {
    "polarity": 0.85,
    "subjectivity": 0.6,
    "classification": "positive"
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Get Query Evaluations
```http
GET /api/evaluations/query/{query_id}
Authorization: Bearer <token>
```

### Get Evaluation
```http
GET /api/evaluations/{evaluation_id}
Authorization: Bearer <token>
```

## Scheduled Tests

### Create Scheduled Test
```http
POST /api/scheduled-tests/
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "name": "Daily Product Test",
  "prompt_template": "What are the benefits of {product}?",
  "llm_providers": ["openai", "anthropic"],
  "topic_id": 1,
  "cron_expression": "0 9 * * *",
  "evaluation_types": ["sentiment", "clarity"]
}
```

**Cron Expression Examples:**
- `0 9 * * *` - Daily at 9:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 0` - Weekly on Sunday at midnight
- `0 0 1 * *` - Monthly on the 1st at midnight

Response:
```json
{
  "id": 1,
  "name": "Daily Product Test",
  "prompt_template": "What are the benefits of {product}?",
  "llm_providers": ["openai", "anthropic"],
  "topic_id": 1,
  "company_id": 1,
  "cron_expression": "0 9 * * *",
  "is_active": true,
  "evaluation_types": ["sentiment", "clarity"],
  "created_at": "2024-01-01T12:00:00Z"
}
```

### List Scheduled Tests
```http
GET /api/scheduled-tests/
Authorization: Bearer <token>
```

### Get Scheduled Test
```http
GET /api/scheduled-tests/{test_id}
Authorization: Bearer <token>
```

### Update Scheduled Test
```http
PUT /api/scheduled-tests/{test_id}?is_active=false
Authorization: Bearer <token>
```

## Health Check

### Check API Health
```http
GET /health
```

Response:
```json
{
  "status": "healthy"
}
```

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider:
- Rate limiting per user/company
- Different tiers for different plan levels
- Monitoring API usage per LLM provider

## Best Practices

1. **Authentication**: Always include the bearer token in the Authorization header
2. **Error Handling**: Handle all possible error responses
3. **Pagination**: Use `skip` and `limit` parameters for large result sets
4. **Filtering**: Use query parameters to filter results (e.g., `topic_id`)
5. **Idempotency**: POST requests create new resources; repeated calls create duplicates
6. **Multi-tenancy**: Data is automatically scoped to your company; you can only access your company's data
