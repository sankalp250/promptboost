# Deployment Checklist

Use this checklist to ensure everything is set up correctly before deploying.

## Pre-Deployment

- [ ] Docker and Docker Compose installed
- [ ] `.env` file created from `env.template`
- [ ] `GROQ_API_KEY` added to `.env`
- [ ] `GOOGLE_API_KEY` added to `.env`
- [ ] Database password set in `.env` (if not using auto-generated)
- [ ] ML models exist in `server/app/ml_models/`:
  - [ ] `preference_model.joblib`
  - [ ] `tfidf_vectorizer.joblib`
  - [ ] If missing, run: `python scripts/train_preference_model.py`

## Files Created

✅ **Dockerfile** - Container configuration for FastAPI server
✅ **docker-compose.yml** - Complete service orchestration
✅ **docker-entrypoint.sh** - Startup script with database wait and migrations
✅ **.dockerignore** - Files excluded from Docker build
✅ **env.template** - Environment variables template
✅ **deploy.sh** - Linux/Mac deployment script
✅ **deploy.ps1** - Windows deployment script
✅ **DEPLOYMENT.md** - Comprehensive deployment guide
✅ **QUICKSTART.md** - Quick start guide
✅ **README.md** - Updated with deployment info

## Deployment Steps

1. [ ] Copy `env.template` to `.env`
2. [ ] Edit `.env` and add API keys
3. [ ] Run deployment script:
   - Linux/Mac: `./deploy.sh`
   - Windows: `.\deploy.ps1`
   - Or manually: `docker-compose up --build -d`
4. [ ] Wait for services to start (check logs: `docker-compose logs -f`)
5. [ ] Verify health check: `curl http://localhost:8000/`
6. [ ] Check API docs: http://localhost:8000/docs

## Post-Deployment Verification

- [ ] Server responds to health check
- [ ] API documentation is accessible
- [ ] Database migrations completed successfully
- [ ] ML models loaded (check server logs)
- [ ] No errors in `docker-compose logs`
- [ ] Can make API requests to `/api/v1/enhance`

## Troubleshooting

If something fails:

1. Check logs: `docker-compose logs -f server`
2. Check database: `docker-compose logs -f db`
3. Verify `.env` file has correct values
4. Check if ports are available (8000, 5432)
5. Review [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section

## Production Checklist

- [ ] Use secure database password
- [ ] Set up database backups
- [ ] Configure reverse proxy (Nginx/Traefik)
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Set resource limits in docker-compose.yml
- [ ] Use secrets management (not .env files)
- [ ] Set up CI/CD pipeline
- [ ] Configure domain name and DNS
