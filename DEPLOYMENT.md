# PromptBoost Deployment Guide

This guide will walk you through deploying the PromptBoost application using Docker.

## Prerequisites

1. **Docker** installed on your system
   - Download from: https://www.docker.com/get-started
   - Verify installation: `docker --version` and `docker-compose --version`

2. **API Keys** ready:
   - Groq API Key (from https://console.groq.com/)
   - Google API Key (for Gemini fallback)

3. **Environment Variables** file (`.env`)

## Step-by-Step Deployment

### Step 1: Create Environment File

**Quick method:** Copy the template:
```bash
# Linux/Mac
cp env.template .env

# Windows (PowerShell)
Copy-Item env.template .env
```

**Or manually create** a `.env` file in the project root directory with the following variables:

```env
# Database Configuration
POSTGRES_USER=promptboost
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=promptboost
POSTGRES_PORT=5432

# Server Configuration
SERVER_PORT=8000
PROJECT_NAME=PromptBoost
PROJECT_DESCRIPTION=Prompt Enhancement Service

# API Keys (REQUIRED)
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

**Important:** Replace `your_secure_password_here`, `your_groq_api_key_here`, and `your_google_api_key_here` with your actual values.

### Step 2: Ensure ML Models Exist

Make sure your ML models are in place:
- `server/app/ml_models/preference_model.joblib`
- `server/app/ml_models/tfidf_vectorizer.joblib`

If these don't exist, you'll need to train them first using:
```bash
python scripts/train_preference_model.py
```

### Step 3: Build and Start Services

Run the following command to build the Docker images and start all services:

```bash
docker-compose up --build
```

This will:
1. Build the server Docker image
2. Pull the PostgreSQL image
3. Start the database container
4. Wait for the database to be healthy
5. Run database migrations
6. Start the FastAPI server

### Step 4: Verify Deployment

Once the services are running, you should see output indicating:
- Database is ready
- Alembic migrations completed
- Server running on `http://0.0.0.0:8000`

Test the deployment:

1. **Health Check:**
   ```bash
   curl http://localhost:8000/
   ```
   Should return: `{"status":"ok","message":"Welcome to PromptBoost"}`

2. **API Documentation:**
   Open your browser and visit: `http://localhost:8000/docs`
   This shows the interactive API documentation.

### Step 5: Run in Background (Optional)

To run the services in the background (detached mode):

```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f server
```

## Common Operations

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ Deletes Database Data)
```bash
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f server
docker-compose logs -f db
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up --build
```

### Access Database
```bash
# Connect to PostgreSQL container
docker-compose exec db psql -U promptboost -d promptboost
```

## Production Deployment Considerations

### 1. Environment Variables Security

For production, use Docker secrets or a secrets management service instead of `.env` files:

```yaml
# In docker-compose.yml
environment:
  GROQ_API_KEY: ${GROQ_API_KEY}
  # Or use Docker secrets
secrets:
  - groq_api_key
```

### 2. Use Production-Grade Database

- Consider using managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
- Update `DATABASE_URL` in environment variables accordingly
- Remove the `db` service from docker-compose.yml if using external database

### 3. Add Reverse Proxy

For production, add Nginx or Traefik as a reverse proxy:

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - server
```

### 4. Enable HTTPS

- Use Let's Encrypt for SSL certificates
- Configure reverse proxy with SSL termination

### 5. Resource Limits

Add resource limits to docker-compose.yml:

```yaml
services:
  server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 6. Logging

Configure logging to external services:
- Use Docker logging drivers
- Integrate with logging services (ELK, CloudWatch, etc.)

### 7. Monitoring

Add monitoring:
- Health check endpoints (already included)
- Prometheus metrics
- Application Performance Monitoring (APM)

### 8. Backup Strategy

Set up database backups:
```bash
# Backup script
docker-compose exec db pg_dump -U promptboost promptboost > backup.sql

# Restore
docker-compose exec -T db psql -U promptboost promptboost < backup.sql
```

## Troubleshooting

### Database Connection Issues

If the server can't connect to the database:
1. Check if database is healthy: `docker-compose ps`
2. Verify DATABASE_URL matches docker-compose environment variables
3. Check database logs: `docker-compose logs db`

### Migration Failures

If migrations fail:
1. Check database logs: `docker-compose logs db`
2. Manually run migrations:
   ```bash
   docker-compose exec server alembic upgrade head
   ```

### Port Already in Use

If port 8000 or 5432 is already in use:
1. Change ports in `.env` file
2. Update `SERVER_PORT` and `POSTGRES_PORT` accordingly

### ML Models Not Found

If you see errors about missing ML models:
1. Ensure models exist in `server/app/ml_models/`
2. Train models if needed: `python scripts/train_preference_model.py`
3. Copy models to the correct location

### API Key Issues

If you get authentication errors:
1. Verify API keys in `.env` file
2. Check API keys are valid and have proper permissions
3. Review server logs: `docker-compose logs server`

## Next Steps After Deployment

1. **Test the API endpoints** using the interactive docs at `/docs`
2. **Monitor the application** for any errors or issues
3. **Set up backups** for your database
4. **Configure monitoring** and alerting
5. **Update client application** to point to the deployed server URL

## Deployment to Cloud Platforms

### AWS (EC2/ECS)

1. Push Docker image to ECR
2. Use ECS Fargate or EC2 with docker-compose
3. Set up RDS for managed PostgreSQL
4. Configure ALB for load balancing

### Google Cloud Platform

1. Use Cloud Run for serverless deployment
2. Use Cloud SQL for managed PostgreSQL
3. Configure Cloud Load Balancer

### Azure

1. Use Azure Container Instances or App Service
2. Use Azure Database for PostgreSQL
3. Configure Application Gateway

### DigitalOcean

1. Use App Platform or Droplets
2. Use Managed PostgreSQL
3. Configure Load Balancer

## Support

For issues or questions:
- Check server logs: `docker-compose logs server`
- Check database logs: `docker-compose logs db`
- Review the API docs at `http://localhost:8000/docs`
