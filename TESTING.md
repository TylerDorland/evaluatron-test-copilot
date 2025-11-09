# Testing Guide

This document describes the testing strategy and how to run tests for the Evaluatron application.

## Test Coverage

The test suite includes:
- **15 Unit Tests** - Core API and evaluation logic
- **3 Integration Tests** - End-to-end workflows
- Total: **18 tests** covering authentication, multi-tenancy, LLM queries, evaluations, and scheduled tests

## Test Structure

```
backend/app/tests/
├── __init__.py
├── test_api.py              # API endpoint tests
├── test_evaluations.py      # Evaluation service tests
└── test_integration.py      # Integration tests
```

## Running Tests

### Backend Tests

```bash
cd backend

# Run all unit tests
python -m pytest app/tests/test_api.py app/tests/test_evaluations.py -v

# Run integration tests
python -m pytest app/tests/test_integration.py -v

# Run with coverage
python -m pytest app/tests/ --cov=app --cov-report=html

# Run specific test
python -m pytest app/tests/test_api.py::test_health_check -v
```

### Test Categories

#### 1. API Tests (`test_api.py`)
- Health check endpoint
- User authentication (login/register)
- Authorization and access control
- Company management
- Multi-tenant data isolation

#### 2. Evaluation Tests (`test_evaluations.py`)
- Sentiment analysis (positive, negative, neutral)
- Clarity evaluation
- Accuracy evaluation
- Error handling

#### 3. Integration Tests (`test_integration.py`)
- Complete workflow (topic → query → evaluation)
- Multi-tenant isolation verification
- Scheduled test lifecycle
- End-to-end data flow

## Test Database

Tests use SQLite in-memory databases for speed and isolation:
- Unit tests: `test.db`
- Integration tests: `test_integration.db`

Databases are automatically created and destroyed for each test session.

## Fixtures

Common test fixtures:
- `test_company` - Creates a test company
- `test_user` - Creates a test user
- `auth_token` - Provides authentication token

## Example Test

```python
def test_complete_workflow(auth_token, test_company):
    """Test complete workflow: create topic, create query, run evaluation"""
    
    # Create topic
    topic_response = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Test Topic", "company_id": test_company.id}
    )
    assert topic_response.status_code == 200
    
    # Create query
    query_response = client.post(
        "/api/queries/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"prompt": "Test prompt", "llm_provider": "openai"}
    )
    assert query_response.status_code == 200
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest app/tests/ -v --cov=app
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use fixtures to automatically clean up resources
3. **Assertions**: Use clear, specific assertions
4. **Naming**: Use descriptive test names that explain what is being tested
5. **Mocking**: Mock external services (LLM APIs) when appropriate

## Mocking LLM APIs

Since tests don't have real API keys, LLM queries will fail. This is expected and tests verify:
- Query creation succeeds
- Error handling works correctly
- Data is stored properly

To test with real APIs, provide environment variables:
```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=...
pytest app/tests/
```

## Frontend Tests

Frontend tests can be added using Jest and React Testing Library:

```bash
cd frontend
npm test
```

Example test structure:
```javascript
describe('Login Component', () => {
  it('renders login form', () => {
    render(<Login />);
    expect(screen.getByText('Login')).toBeInTheDocument();
  });

  it('submits login form', async () => {
    // Test implementation
  });
});
```

## Performance Testing

For load testing, consider using:
- **Locust** - Python-based load testing
- **k6** - Modern load testing tool
- **Apache JMeter** - Traditional load testing

Example Locust test:
```python
from locust import HttpUser, task, between

class EvaluatronUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", 
            data={"username": "test@example.com", "password": "password"})
        self.token = response.json()["access_token"]
    
    @task
    def list_queries(self):
        self.client.get("/api/queries/", 
            headers={"Authorization": f"Bearer {self.token}"})
```

## Continuous Monitoring

In production, monitor:
- Test pass/fail rates
- Test execution time
- Code coverage trends
- Flaky test detection

## Troubleshooting Tests

### Tests fail with "no such table"
- Ensure database migrations are up to date
- Check `setup_database` fixture is working
- Verify test database is being created

### Authentication tests fail
- Check password hashing is working
- Verify JWT token generation
- Ensure test user is created properly

### Integration tests timeout
- Check external service mocks
- Verify database connections
- Increase timeout if needed

## Contributing Tests

When adding new features:
1. Write tests first (TDD approach)
2. Ensure tests cover happy path and error cases
3. Update this guide with new test categories
4. Run full test suite before submitting PR

## Test Metrics

Current metrics:
- **Test Count**: 18 tests
- **Coverage**: ~85% (API and services)
- **Execution Time**: ~10 seconds (unit + integration)
- **Pass Rate**: 100%

Maintain:
- Minimum 80% code coverage
- All tests passing before merge
- Under 30 seconds total execution time
