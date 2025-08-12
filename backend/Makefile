# AI Provenance Tool - Development Commands
# Usage: make <command>

.PHONY: dev install test clean lint format help

# Default target
help:
	@echo "AI Provenance Tool - Available Commands:"
	@echo ""
	@echo "  make dev        - Start development server"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean up generated files"
	@echo "  make migrate    - Run database migrations"
	@echo "  make seed       - Seed database with sample data"
	@echo ""

# Start development server
dev:
	@echo "🚀 Starting AI Provenance Tool Development Server..."
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@echo "✅ Activating virtual environment and starting server..."
	@echo "📚 API Documentation: http://localhost:8000/docs"
	@echo "🏥 Health Check: http://localhost:8000/health"
	@echo ""
	@source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Install dependencies
install:
	@echo "📦 Setting up virtual environment and installing dependencies..."
	@python3 -m venv venv
	@source venv/bin/activate && pip install --upgrade pip
	@source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Installation complete!"

# Run tests
test:
	@echo "🧪 Running tests..."
	@source venv/bin/activate && pytest

# Run linting
lint:
	@echo "🔍 Running linting..."
	@source venv/bin/activate && flake8 app/

# Format code
format:
	@echo "🎨 Formatting code..."
	@source venv/bin/activate && black app/

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@rm -rf logs/
	@echo "✅ Cleanup complete!"

# Run database migrations
migrate:
	@echo "🗄️  Running database migrations..."
	@source venv/bin/activate && alembic upgrade head

# Seed database
seed:
	@echo "🌱 Seeding database with sample data..."
	@source venv/bin/activate && python app/utils/seed_data.py

# Production server
prod:
	@echo "🚀 Starting production server..."
	@source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000