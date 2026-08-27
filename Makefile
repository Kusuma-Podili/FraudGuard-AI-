.PHONY: install build run test benchmark clean lint

PYTHON ?= python
PIP ?= pip
NPM ?= npm

install:
	@echo "Installing Python dependencies..."
	$(PIP) install -r backend/requirements.txt
	@echo "Installing Frontend dependencies..."
	cd frontend && $(NPM) install

build:
	@echo "Building Next.js frontend..."
	cd frontend && $(NPM) run build
	@echo "Building Docker images..."
	docker build -f Dockerfile.backend -t fraudguard-backend:latest .
	docker build -f Dockerfile.simulator -t fraudguard-simulator:latest .

run:
	@echo "Starting FraudGuard AI Decision Gateway..."
	$(PYTHON) main.py

test:
	@echo "Running all unit, integration, and E2E test suites..."
	$(PYTHON) -m unittest discover -s ml_engine/tests
	$(PYTHON) -m unittest discover -s backend/tests
	$(PYTHON) -m unittest discover -s simulator/tests
	$(PYTHON) -m unittest discover -s tests/e2e

benchmark:
	@echo "Running sub-20ms SLA latency benchmark..."
	$(PYTHON) -m simulator.cli benchmark --requests 1000 --concurrency 8

clean:
	@echo "Cleaning caches and temporary artifacts..."
	rm -rf .pytest_cache htmlcov .coverage frontend/.next
