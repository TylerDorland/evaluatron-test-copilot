# Evaluatron - LLM Response Tracking & Evaluation Platform

A comprehensive multi-tenant platform for tracking, evaluating, and analyzing responses from multiple LLM providers (Anthropic, OpenAI, Google).

## Features

- **Multi-Tenant Architecture**: Support for multiple companies, users, and topics
- **Multiple LLM Providers**: Query Anthropic, OpenAI, and Google models
- **Evaluation Engine**: Built-in sentiment, accuracy, and clarity evaluations
- **Scheduled Tests**: Recurring tests with cron expressions
- **Analytics Dashboard**: Visualize results and performance over time
- **RESTful API**: Full-featured FastAPI backend with automatic documentation
- **Modern Frontend**: React-based UI with real-time updates

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy + PostgreSQL
- Alembic (migrations)
- JWT Authentication
- Langsmith Integration (optional)

### Frontend
- React 18
- Recharts (visualizations)
- Axios
- React Router

### Infrastructure
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

## Quick Start

### Prerequisites
- Docker and Docker Compose
- API keys for LLM providers (optional for testing)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd evaluatron-test-copilot
```

2. Set up environment variables:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Default Credentials

```
Admin: admin@acme.com / password123
User1: user1@acme.com / password123
User2: user2@techstart.com / password123
User3: user3@global.com / password123
```

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed test data
python seed_data.py

# Run tests
pytest

# Start development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Key Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/companies/` - List companies
- `POST /api/topics/` - Create topic
- `POST /api/queries/` - Create and execute LLM query
- `POST /api/evaluations/` - Run evaluation on query
- `POST /api/scheduled-tests/` - Create scheduled test

## Architecture

### Multi-Tenant Design

The application uses a shared database with tenant isolation:
- Each company has its own data space
- Users belong to a single company
- Data access is automatically scoped by company_id
- Row-level security ensures data isolation

### LLM Integration

The system uses a factory pattern for LLM clients:
- `AnthropicClient` - Claude models
- `OpenAIClient` - GPT models
- `GoogleClient` - Gemini models

Each client implements a common interface for consistent behavior.

### Evaluation System

Three built-in evaluation types:
1. **Sentiment** - Polarity analysis (-1 to 1)
2. **Clarity** - Readability metrics (0 to 1)
3. **Accuracy** - Keyword matching and heuristics (0 to 1)

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Environment-based secrets
- Multi-tenant data isolation
- Input validation with Pydantic

## Testing

### Backend Tests

```bash
cd backend
pytest --cov=app tests/
```

Tests cover:
- Authentication and authorization
- API endpoints
- Evaluation algorithms
- Database models

### Frontend Tests

```bash
cd frontend
npm test
```

## Deployment

### Production Considerations

1. **Environment Variables**: Set production values for:
   - `SECRET_KEY` (use a strong random key)
   - `DATABASE_URL` (production database)
   - LLM API keys
   - `CORS_ORIGINS` (production frontend URL)

2. **Database**: 
   - Use managed PostgreSQL service
   - Enable SSL connections
   - Regular backups

3. **Security**:
   - Enable HTTPS
   - Set secure CORS origins
   - Use secrets management (AWS Secrets Manager, etc.)
   - Enable rate limiting

4. **Scaling**:
   - Use Redis for caching and session storage
   - Consider Celery for background tasks
   - Load balance multiple backend instances

## Monitoring

The platform includes:
- Health check endpoint: `/health`
- Performance metrics (latency tracking)
- Query status tracking
- Evaluation results logging

## Future Enhancements

- [ ] Real-time scheduler execution
- [ ] Advanced visualization options
- [ ] Custom evaluation metrics
- [ ] Export capabilities (CSV, PDF)
- [ ] Webhook notifications
- [ ] A/B testing support
- [ ] Cost tracking per provider
- [ ] Team collaboration features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.