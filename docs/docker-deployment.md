# Docker Deployment Guide

This guide covers deploying the EASM platform using Docker and Docker Compose for all three tiers.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ RAM (Tier A), 4GB+ RAM (Tier B), 8GB+ RAM (Tier C)
- Linux, macOS, or Windows with WSL2

## Quick Start (Tier A)

```bash
# Clone repository
git clone <repository-url>
cd Easm

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Access the application
open http://localhost:8000/docs
```

## Tier-Specific Deployment

### Tier A - Open Source (SQLite, Single Container)

**Best for:** Individual users, small teams, development

```bash
# Using default docker-compose.yml
docker-compose up -d

# OR using explicit tier file
docker-compose -f docker-compose.tier-a.yml up -d
```

**Services:**
- Backend API (port 8000)

**Storage:**
- SQLite database in Docker volume
- Nuclei templates in shared volume

**First Time Setup:**
```bash
# Initialize default admin user
curl http://localhost:8000/api/v1/auth/init

# Login credentials:
# Username: admin
# Password: admin (CHANGE THIS!)
```

### Tier B - Business Edition (PostgreSQL, Redis, Celery)

**Best for:** Medium-sized organizations, on-premise deployments

```bash
# Copy environment template
cp .env.docker .env

# Edit .env and set:
# - SECRET_KEY
# - JWT_SECRET_KEY
# - POSTGRES_PASSWORD

# Start services
docker-compose -f docker-compose.tier-b.yml up -d

# Check all services are healthy
docker-compose -f docker-compose.tier-b.yml ps

# View logs
docker-compose -f docker-compose.tier-b.yml logs -f
```

**Services:**
- Backend API (port 8000)
- PostgreSQL database (port 5432)
- Redis (port 6379)
- Celery worker (background tasks)
- Celery beat (scheduled scans)

**Database Initialization:**
```bash
# Database tables are created automatically on first run
# Check logs to verify:
docker-compose -f docker-compose.tier-b.yml logs backend | grep "Database initialized"

# Initialize admin user
curl http://localhost:8000/api/v1/auth/init
```

### Tier C - Enterprise Edition (Multi-tenant, Scaled)

**Best for:** SaaS deployments, enterprise organizations

```bash
# Copy environment template
cp .env.docker .env

# Edit .env with production values
nano .env

# Start services
docker-compose -f docker-compose.tier-c.yml up -d

# Verify all services
docker-compose -f docker-compose.tier-c.yml ps

# Check health
curl http://localhost:80/health
```

**Services:**
- Backend API (2 replicas, load balanced)
- PostgreSQL database
- Redis (with caching)
- Celery workers (3 replicas, distributed scanning)
- Celery beat (scheduled scans)
- Flower (Celery monitoring on port 5555)
- Nginx (reverse proxy on port 80)

**Scaling:**
```bash
# Scale backend
docker-compose -f docker-compose.tier-c.yml up -d --scale backend=4

# Scale workers
docker-compose -f docker-compose.tier-c.yml up -d --scale celery-worker=5
```

## Configuration

### Environment Variables

Key variables to configure:

```env
# Security (REQUIRED - change in production)
SECRET_KEY=<generate-random-key>
JWT_SECRET_KEY=<generate-random-key>
POSTGRES_PASSWORD=<strong-password>

# Application
APP_TIER=A  # or B or C
DEBUG=false

# Optional: Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password
EMAIL_FROM=noreply@example.com
```

### Generate Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32

# Generate POSTGRES_PASSWORD
openssl rand -base64 32
```

## Management Commands

### Start/Stop

```bash
# Start (Tier A)
docker-compose up -d

# Start (Tier B)
docker-compose -f docker-compose.tier-b.yml up -d

# Start (Tier C)
docker-compose -f docker-compose.tier-c.yml up -d

# Stop
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Database Management

```bash
# Tier B/C: Connect to PostgreSQL
docker-compose exec postgres psql -U easm -d easm

# Backup database
docker-compose exec postgres pg_dump -U easm easm > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U easm easm
```

### Update Nuclei Templates

```bash
# Tier A
docker-compose exec backend nuclei -update-templates

# Tier B
docker-compose -f docker-compose.tier-b.yml exec backend nuclei -update-templates

# Tier C
docker-compose -f docker-compose.tier-c.yml exec backend nuclei -update-templates
```

### Restart Services

```bash
# Restart specific service
docker-compose restart backend

# Restart all
docker-compose restart
```

## Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Check which tier features are enabled
curl http://localhost:8000/health | jq '.features'
```

### Celery Monitoring (Tier B/C)

```bash
# View worker status
docker-compose exec celery-worker celery -A app.workers.celery_app inspect active

# View scheduled tasks
docker-compose exec celery-beat celery -A app.workers.celery_app inspect scheduled

# Tier C: Access Flower web UI
open http://localhost:5555
```

### Resource Usage

```bash
# View resource usage
docker stats

# Specific container
docker stats easm-backend
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait for health check
# 2. Missing environment variables - check .env
# 3. Port already in use - change port mapping
```

### Database connection errors

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check health
docker-compose exec postgres pg_isready -U easm

# View PostgreSQL logs
docker-compose logs postgres
```

### Celery workers not processing tasks

```bash
# Check worker logs
docker-compose logs celery-worker

# Verify Redis connection
docker-compose exec redis redis-cli ping

# Restart workers
docker-compose restart celery-worker
```

### Nuclei scans failing

```bash
# Verify Nuclei installation
docker-compose exec backend nuclei -version

# Update templates
docker-compose exec backend nuclei -update-templates

# Check permissions
docker-compose exec backend ls -la /usr/local/bin/nuclei
```

## Production Recommendations

### Security

1. **Change default passwords**
   ```bash
   # Generate strong secrets
   openssl rand -hex 32
   ```

2. **Use HTTPS**
   - Configure SSL certificates in Nginx
   - Use Let's Encrypt for free certificates

3. **Restrict database access**
   - Remove port mappings for PostgreSQL/Redis
   - Use Docker networks only

4. **Regular updates**
   ```bash
   # Update Nuclei templates weekly
   docker-compose exec backend nuclei -update-templates
   ```

### Performance

1. **Resource limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

2. **Scale workers** (Tier C)
   ```bash
   docker-compose up -d --scale celery-worker=5
   ```

3. **Database tuning**
   - Adjust PostgreSQL `shared_buffers`
   - Enable connection pooling

### Backup

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U easm easm | gzip > backup_${DATE}.sql.gz
```

### Monitoring

1. **Set up health check monitoring**
2. **Configure log aggregation** (ELK, Loki)
3. **Use Flower for Celery monitoring** (Tier C)

## Upgrading

```bash
# Pull latest images
docker-compose pull

# Rebuild
docker-compose build --no-cache

# Restart with new images
docker-compose up -d

# Check logs for migration messages
docker-compose logs -f backend
```

## Uninstall

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker rmi $(docker images -q 'easm*')
```

## Support

- Documentation: [docs/](.)
- Issues: GitHub Issues
- Security: Report via email

---

For production deployments, consider using Kubernetes or managed container services (ECS, Cloud Run, etc.)
