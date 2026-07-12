# Development Environment Setup

## Prerequisites
- Python 3.11+
- Docker Desktop
- Git
- PostgreSQL client tools
- Redis CLI (optional)

## Step 1: Clone Repository

```bash
git clone https://github.com/company/ecommerce-platform.git
cd ecommerce-platform
```

## Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Start Infrastructure

```bash
# Start PostgreSQL, Redis, RabbitMQ
docker-compose up -d postgres redis rabbitmq

# Verify services are running
docker-compose ps
```

## Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `SECRET_KEY`: Application secret key

## Step 5: Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed test data (optional)
python scripts/seed_data.py
```

## Step 6: Start Services

```bash
# Start all microservices
./scripts/start-dev.sh

# Or start individual services
uvicorn user_service.main:app --reload --port 8001
uvicorn product_service.main:app --reload --port 8002
uvicorn order_service.main:app --reload --port 8003
```

## Step 7: Verify Installation

```bash
# Check service health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Run tests
pytest
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check connection string in `.env`
- Ensure database exists: `psql -U postgres -l`

### Port Conflicts
- Check for processes using ports: `lsof -i :8001`
- Kill conflicting processes or change ports in config

### Dependency Issues
- Update pip: `pip install --upgrade pip`
- Clear cache: `pip cache purge`
- Reinstall: `pip install -r requirements.txt --force-reinstall`

## Related Documents
- [Microservices Architecture](../concepts/microservices.md)
- [Deployment Guide](./deployment-guide.md)
- [REST API Reference](../references/api-reference.md)
