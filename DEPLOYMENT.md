# Deployment Guide

This guide provides instructions for deploying the Evaluatron application in various environments.

## Local Development with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd evaluatron-test-copilot
```

2. **Configure environment variables**
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
LANGSMITH_API_KEY=...
```

3. **Start the application**
```bash
docker-compose up -d
```

4. **Verify deployment**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

5. **View logs**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

6. **Stop the application**
```bash
docker-compose down
```

## Production Deployment

### Prerequisites
- Production-grade database (AWS RDS, Google Cloud SQL, or similar)
- Container orchestration platform (Kubernetes, ECS, or similar)
- Domain name with SSL certificate
- Secret management service (AWS Secrets Manager, HashiCorp Vault, etc.)

### Environment Configuration

Create a production `.env` file with secure values:

```env
# Database - Use production PostgreSQL URL
DATABASE_URL=postgresql://user:password@prod-db.example.com:5432/evaluatron

# Security - Generate strong random keys
SECRET_KEY=<generate-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM API Keys - Use secrets manager
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
GOOGLE_API_KEY=${GOOGLE_API_KEY}

# Langsmith (optional)
LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
LANGSMITH_PROJECT=evaluatron-prod

# Redis - Use production Redis
REDIS_URL=redis://prod-redis.example.com:6379/0

# CORS - Set production frontend URL
CORS_ORIGINS=https://app.example.com,https://www.example.com
```

### Security Best Practices

1. **Use HTTPS**
   - Obtain SSL certificate (Let's Encrypt, AWS ACM, etc.)
   - Configure load balancer or reverse proxy to terminate SSL

2. **Secrets Management**
   - Never commit secrets to version control
   - Use environment-specific secret managers
   - Rotate keys regularly

3. **Database Security**
   - Use strong passwords
   - Enable SSL for database connections
   - Restrict database access by IP
   - Regular backups

4. **Rate Limiting**
   - Implement rate limiting at the API gateway level
   - Consider per-user and per-company limits
   - Monitor for abuse

5. **Network Security**
   - Use private networks for internal services
   - Implement security groups/firewall rules
   - Enable WAF if available

### AWS Deployment Example

#### Using ECS (Elastic Container Service)

1. **Create ECR repositories**
```bash
aws ecr create-repository --repository-name evaluatron-backend
aws ecr create-repository --repository-name evaluatron-frontend
```

2. **Build and push images**
```bash
# Backend
cd backend
docker build -t evaluatron-backend .
docker tag evaluatron-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/evaluatron-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/evaluatron-backend:latest

# Frontend
cd ../frontend
docker build -t evaluatron-frontend .
docker tag evaluatron-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/evaluatron-frontend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/evaluatron-frontend:latest
```

3. **Create RDS PostgreSQL instance**
```bash
aws rds create-db-instance \
  --db-instance-identifier evaluatron-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username evaluatron \
  --master-user-password <strong-password> \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name evaluatron-subnet
```

4. **Create ECS task definitions and services**
   - Use AWS Console or CloudFormation/Terraform
   - Configure environment variables from Secrets Manager
   - Set up Application Load Balancer
   - Configure auto-scaling

### Kubernetes Deployment Example

1. **Create namespace**
```bash
kubectl create namespace evaluatron
```

2. **Create secrets**
```bash
kubectl create secret generic evaluatron-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=secret-key=... \
  --from-literal=anthropic-api-key=... \
  --from-literal=openai-api-key=... \
  --from-literal=google-api-key=... \
  -n evaluatron
```

3. **Apply Kubernetes manifests**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: evaluatron-backend
  namespace: evaluatron
spec:
  replicas: 3
  selector:
    matchLabels:
      app: evaluatron-backend
  template:
    metadata:
      labels:
        app: evaluatron-backend
    spec:
      containers:
      - name: backend
        image: <your-registry>/evaluatron-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: evaluatron-secrets
              key: database-url
        # ... other environment variables
```

4. **Create services and ingress**
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: evaluatron-backend
  namespace: evaluatron
spec:
  selector:
    app: evaluatron-backend
  ports:
  - port: 80
    targetPort: 8000
```

### Database Migrations

Run migrations before deploying new versions:

```bash
# Using Docker
docker-compose exec backend alembic upgrade head

# Using kubectl
kubectl exec -it <backend-pod> -n evaluatron -- alembic upgrade head

# Using ECS task
aws ecs run-task --task-definition evaluatron-migration --cluster evaluatron
```

### Monitoring and Logging

1. **Application Logs**
   - Use structured logging (JSON format)
   - Centralize logs (CloudWatch, ELK, etc.)
   - Set up log retention policies

2. **Metrics**
   - Track API response times
   - Monitor LLM API usage and costs
   - Database connection pool metrics
   - Error rates

3. **Alerts**
   - Set up alerts for:
     - High error rates
     - Slow API responses
     - Database connection failures
     - LLM API quota limits

4. **Health Checks**
   - Configure load balancer health checks to `/health`
   - Monitor database connectivity
   - Check external API availability

### Backup and Recovery

1. **Database Backups**
   - Enable automated daily backups
   - Test restore procedures regularly
   - Keep backups for at least 30 days

2. **Application State**
   - Version control all code
   - Tag releases
   - Document deployment procedures

### Scaling Considerations

1. **Horizontal Scaling**
   - Backend: Scale based on CPU/memory usage
   - Frontend: Use CDN for static assets
   - Database: Use read replicas for read-heavy workloads

2. **Caching**
   - Use Redis for session storage
   - Cache frequent queries
   - Implement rate limiting with Redis

3. **Async Processing**
   - Use Celery for background tasks
   - Queue LLM requests for batch processing
   - Implement scheduled test execution

### Cost Optimization

1. **LLM API Costs**
   - Monitor usage per company/user
   - Set budget limits
   - Cache common responses
   - Use cheaper models for simple queries

2. **Infrastructure**
   - Right-size containers and instances
   - Use spot instances for non-critical workloads
   - Implement auto-scaling policies

### Maintenance

1. **Regular Updates**
   - Update dependencies monthly
   - Apply security patches promptly
   - Test updates in staging environment

2. **Database Maintenance**
   - Vacuum and analyze regularly
   - Monitor table sizes and indexes
   - Optimize slow queries

3. **Monitoring Review**
   - Review logs and metrics weekly
   - Adjust alerts as needed
   - Plan capacity based on growth

## Troubleshooting

### Backend won't start
- Check DATABASE_URL is correct
- Verify all required environment variables are set
- Check database is accessible
- Review logs for specific errors

### Frontend can't connect to backend
- Verify CORS_ORIGINS includes frontend URL
- Check API URL in frontend environment
- Ensure backend is accessible from frontend

### Database connection errors
- Verify database credentials
- Check network connectivity
- Ensure database server is running
- Review connection pool settings

### LLM API errors
- Verify API keys are valid
- Check API rate limits
- Monitor API quotas
- Review error messages in logs

## Support

For deployment assistance, open an issue on GitHub with:
- Deployment environment details
- Error messages and logs
- Configuration (sanitized)
- Steps to reproduce
