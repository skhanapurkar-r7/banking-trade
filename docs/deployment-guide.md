# Deployment Guide

## Overview

This guide covers deploying the Trade Store application to various environments, from development to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Database Migration](#database-migration)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Development Environment

- Python 3.10+
- Node.js 18+
- Poetry
- npm
- Git

### Production Environment

- Linux server (Ubuntu 20.04+ recommended)
- Docker (optional but recommended)
- Nginx or Apache
- SSL certificate
- Domain name

## Environment Configuration

### Environment Variables

#### Backend (.env)

**Development:**
```env
DATABASE_URL=sqlite:///./trades.db
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Production:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/tradestore
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

#### Frontend (.env)

**Development:**
```env
VITE_API_BASE_URL=http://localhost:8000
```

**Production:**
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

## Backend Deployment

### Option 1: Traditional Server Deployment

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install PostgreSQL (recommended for production)
sudo apt install postgresql postgresql-contrib -y
```

#### 2. Application Setup

```bash
# Clone repository
git clone <repository-url>
cd trade-store/backend

# Install dependencies
poetry install --no-dev

# Create .env file
cp .env.example .env
nano .env  # Edit with production values

# Initialize database
poetry run python -c "from app.repositories.database import init_db; init_db()"
```

#### 3. Run with Gunicorn

```bash
# Install Gunicorn
poetry add gunicorn

# Run application
poetry run gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### 4. Create Systemd Service

```bash
sudo nano /etc/systemd/system/tradestore.service
```

```ini
[Unit]
Description=Trade Store API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/trade-store/backend
Environment="PATH=/var/www/trade-store/backend/.venv/bin"
ExecStart=/var/www/trade-store/backend/.venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable tradestore
sudo systemctl start tradestore
sudo systemctl status tradestore
```

#### 5. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/tradestore
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tradestore /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal is configured automatically
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/tradestore
      - LOG_LEVEL=INFO
      - CORS_ORIGINS=https://yourdomain.com
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=tradestore
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 3. Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 3: Cloud Platform Deployment

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.10 trade-store-api

# Create environment
eb create production

# Deploy
eb deploy

# Open application
eb open
```

#### Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create trade-store-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Open app
heroku open
```

#### Google Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/trade-store-api

# Deploy
gcloud run deploy trade-store-api \
  --image gcr.io/PROJECT_ID/trade-store-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Frontend Deployment

### Option 1: Static Hosting

#### 1. Build Application

```bash
cd frontend
npm run build
```

This creates a `dist/` folder with static files.

#### 2. Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod --dir=dist
```

**netlify.toml:**
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### 3. Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

**vercel.json:**
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

#### 4. Deploy to AWS S3 + CloudFront

```bash
# Build
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

### Option 2: Nginx Static Hosting

```bash
# Copy build files
sudo cp -r dist/* /var/www/html/

# Configure Nginx
sudo nano /etc/nginx/sites-available/tradestore-frontend
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tradestore-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Option 3: Docker Deployment

#### Dockerfile

```dockerfile
# frontend/Dockerfile

# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### nginx.conf

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Deploy

```bash
# Build image
docker build -t trade-store-frontend .

# Run container
docker run -d -p 80:80 trade-store-frontend
```

## Database Migration

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql

CREATE DATABASE tradestore;
CREATE USER tradestore_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE tradestore TO tradestore_user;
\q
```

### Migrate from SQLite to PostgreSQL

```bash
# Export SQLite data
sqlite3 trades.db .dump > trades.sql

# Import to PostgreSQL
psql -U tradestore_user -d tradestore < trades.sql
```

### Using Alembic for Migrations

```bash
# Install Alembic
poetry add alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Monitoring and Logging

### Application Logging

#### Configure Logging

```python
# app/core/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[handler, logging.StreamHandler()]
    )
```

### Error Tracking with Sentry

```bash
# Install Sentry SDK
poetry add sentry-sdk[fastapi]
```

```python
# app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### Monitoring with Prometheus

```bash
# Install prometheus client
poetry add prometheus-fastapi-instrumentator
```

```python
# app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### Health Checks

```python
@app.get("/health")
def health_check():
    # Check database connection
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Security Considerations

### Backend Security

1. **Environment Variables**
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault)

2. **HTTPS Only**
   ```python
   if not request.url.scheme == "https":
       return RedirectResponse(url=str(request.url).replace("http://", "https://"))
   ```

3. **Rate Limiting**
   ```bash
   poetry add slowapi
   ```
   
   ```python
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.get("/api/v1/trades")
   @limiter.limit("100/minute")
   def get_trades():
       pass
   ```

4. **CORS Configuration**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE"],
       allow_headers=["*"],
   )
   ```

### Frontend Security

1. **Content Security Policy**
   ```html
   <meta http-equiv="Content-Security-Policy" 
         content="default-src 'self'; script-src 'self' 'unsafe-inline';">
   ```

2. **Environment Variables**
   - Prefix with `VITE_` for public variables
   - Never expose secrets in frontend

3. **HTTPS Only**
   - Enforce HTTPS in production
   - Use HSTS headers

## Performance Optimization

### Backend

1. **Database Connection Pooling**
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=0
   )
   ```

2. **Caching with Redis**
   ```bash
   poetry add redis
   ```
   
   ```python
   from redis import Redis
   
   redis_client = Redis(host='localhost', port=6379)
   
   @app.get("/api/v1/trades")
   def get_trades():
       cached = redis_client.get("trades")
       if cached:
           return json.loads(cached)
       # ... fetch from database
       redis_client.setex("trades", 300, json.dumps(trades))
   ```

3. **Async Endpoints**
   ```python
   @app.get("/api/v1/trades")
   async def get_trades():
       # Use async database operations
       pass
   ```

### Frontend

1. **Code Splitting**
   ```typescript
   const AboutPage = lazy(() => import('./pages/AboutPage'));
   ```

2. **Asset Optimization**
   - Compress images
   - Minify CSS/JS
   - Use CDN for static assets

3. **Caching Strategy**
   ```typescript
   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 5 * 60 * 1000, // 5 minutes
         cacheTime: 10 * 60 * 1000, // 10 minutes
       },
     },
   });
   ```

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump -U tradestore_user tradestore > backup_$(date +%Y%m%d).sql

# Automated daily backups
0 2 * * * pg_dump -U tradestore_user tradestore > /backups/backup_$(date +\%Y\%m\%d).sql
```

### Application Backup

```bash
# Backup application files
tar -czf app_backup_$(date +%Y%m%d).tar.gz /var/www/trade-store

# Backup to S3
aws s3 cp backup.sql s3://your-backup-bucket/
```

## Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check logs
sudo journalctl -u tradestore -f

# Check port availability
sudo netstat -tulpn | grep 8000

# Check environment variables
poetry run python -c "from app.core.config import settings; print(settings.database_url)"
```

#### Database Connection Errors

```bash
# Test database connection
psql -U tradestore_user -d tradestore -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### High Memory Usage

```bash
# Check process memory
ps aux | grep gunicorn

# Reduce workers
# In systemd service file, reduce --workers count
```

#### Slow Response Times

```bash
# Check database queries
# Enable query logging in PostgreSQL

# Check application logs
tail -f logs/app.log

# Monitor with htop
htop
```

## Rollback Procedure

### Application Rollback

```bash
# Git rollback
git checkout previous-version-tag
git push origin main --force

# Docker rollback
docker-compose down
docker-compose up -d --build
```

### Database Rollback

```bash
# Restore from backup
psql -U tradestore_user -d tradestore < backup_20240210.sql

# Alembic downgrade
alembic downgrade -1
```

## Conclusion

This deployment guide covers various deployment scenarios. Choose the approach that best fits your infrastructure and requirements. Always test deployments in a staging environment before production.
