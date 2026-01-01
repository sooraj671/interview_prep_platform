.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate seed

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Start development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean cache files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up   - Start services with Docker"
	@echo "  docker-down - Stop Docker services"
	@echo "  migrate     - Run database migrations"
	@echo "  seed        - Seed database with initial data"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	flake8 app/ tests/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/

docker-build:
	docker build -t interview-prep-platform .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

seed:
	python scripts/seed_data.py

setup: docker-up migrate seed
	@echo "Development environment is ready!"

logs:
	docker-compose logs -f app

shell:
	docker-compose exec app bash
