# FraudGuard AI: Production Operations Runbook

## 1. Quick Start (Docker Compose)

```bash
# Clone repository
git clone <REPO_URL>
cd credit

# Build and start all services
docker compose up --build -d

# Check service status
docker compose ps

# View backend logs
docker compose logs -f backend
```

## 2. Ports & Endpoints
- **Frontend Dashboard**: `http://localhost:3000`
- **Backend API & Swagger Docs**: `http://localhost:8000/api/v1/docs`
- **Health Check Probe**: `http://localhost:8000/api/v1/health`

## 3. Seed Credentials
- **Admin**: `admin@fraudguard.ai` / `Admin@FraudGuard2026`
- **Analyst**: `analyst@fraudguard.ai` / `Analyst@FraudGuard2026`

## 4. Running Tests
```bash
# Run all Python unit, integration, and E2E tests
python -m unittest discover -s ml_engine/tests
python -m unittest discover -s backend/tests
python -m unittest discover -s simulator/tests
python -m unittest discover -s tests/e2e
```
