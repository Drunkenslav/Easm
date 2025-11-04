# EASM Platform - Makefile
# Quick commands for common operations

.PHONY: help build up down logs clean test lint

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "EASM Platform - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Tier A commands
build-a: ## Build Tier A (Open Source) Docker image
	docker-compose build

up-a: ## Start Tier A services
	docker-compose up -d
	@echo "Tier A started. Access at http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down-a: ## Stop Tier A services
	docker-compose down

logs-a: ## View Tier A logs
	docker-compose logs -f

# Tier B commands
build-b: ## Build Tier B (Business) Docker images
	docker-compose -f docker-compose.tier-b.yml build

up-b: ## Start Tier B services
	docker-compose -f docker-compose.tier-b.yml up -d
	@echo "Tier B started. Access at http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down-b: ## Stop Tier B services
	docker-compose -f docker-compose.tier-b.yml down

logs-b: ## View Tier B logs
	docker-compose -f docker-compose.tier-b.yml logs -f

# Tier C commands
build-c: ## Build Tier C (Enterprise) Docker images
	docker-compose -f docker-compose.tier-c.yml build

up-c: ## Start Tier C services
	docker-compose -f docker-compose.tier-c.yml up -d
	@echo "Tier C started:"
	@echo "  API: http://localhost:80"
	@echo "  Docs: http://localhost:80/docs"
	@echo "  Flower: http://localhost:5555"

down-c: ## Stop Tier C services
	docker-compose -f docker-compose.tier-c.yml down

logs-c: ## View Tier C logs
	docker-compose -f docker-compose.tier-c.yml logs -f

# Common commands (default to Tier A)
build: build-a ## Build Docker images (Tier A)

up: up-a ## Start services (Tier A)

down: down-a ## Stop services (Tier A)

logs: logs-a ## View logs (Tier A)

restart: ## Restart services (Tier A)
	docker-compose restart

ps: ## Show running containers
	docker-compose ps

# Maintenance
init-user: ## Initialize default admin user
	curl -X GET http://localhost:8000/api/v1/auth/init

update-nuclei: ## Update Nuclei templates
	docker-compose exec backend nuclei -update-templates

backup-db: ## Backup database (Tier B/C only)
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U easm easm > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup created in backups/"

clean: ## Remove containers, volumes, and images
	docker-compose down -v
	docker-compose -f docker-compose.tier-b.yml down -v
	docker-compose -f docker-compose.tier-c.yml down -v
	@echo "Cleaned up all Docker resources"

# Development
dev: ## Start in development mode (hot reload)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

install: ## Install Python dependencies
	cd backend && pip install -r requirements.txt

test: ## Run tests
	cd backend && pytest

lint: ## Lint code
	cd backend && black app/ && flake8 app/

# Utilities
shell: ## Open shell in backend container
	docker-compose exec backend /bin/sh

db-shell: ## Open PostgreSQL shell (Tier B/C)
	docker-compose -f docker-compose.tier-b.yml exec postgres psql -U easm -d easm

redis-cli: ## Open Redis CLI (Tier B/C)
	docker-compose -f docker-compose.tier-b.yml exec redis redis-cli

health: ## Check application health
	@curl -s http://localhost:8000/health | jq '.'

# Security
gen-keys: ## Generate secret keys for .env
	@echo "SECRET_KEY=$$(openssl rand -hex 32)"
	@echo "JWT_SECRET_KEY=$$(openssl rand -hex 32)"
	@echo "POSTGRES_PASSWORD=$$(openssl rand -base64 32)"
