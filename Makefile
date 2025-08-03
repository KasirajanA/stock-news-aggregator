# Stock News Aggregator Makefile

.PHONY: help dev backend frontend install build test migrate shell clean

help: ## Show this help message
	@echo "Stock News Aggregator - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start both backend and frontend servers
	@echo "🚀 Starting Stock News Aggregator..."
	@concurrently "make backend" "make frontend"

backend: ## Start Django backend server
	@echo "📡 Starting Django Backend (http://localhost:8000)..."
	@cd backend && python manage.py runserver 0.0.0.0:8000

frontend: ## Start React frontend server
	@echo "🌐 Starting React Frontend (http://localhost:3001)..."
	@cd frontend && npm start

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	@npm install
	@cd frontend && npm install

build: ## Build frontend for production
	@echo "🔨 Building frontend..."
	@cd frontend && npm run build

test: ## Run backend tests
	@echo "🧪 Running tests..."
	@cd backend && python manage.py test

migrate: ## Run database migrations
	@echo "🗄️ Running migrations..."
	@cd backend && python manage.py migrate

makemigrations: ## Create new migrations
	@echo "📝 Creating migrations..."
	@cd backend && python manage.py makemigrations

shell: ## Open Django shell
	@echo "🐍 Opening Django shell..."
	@cd backend && python manage.py shell

superuser: ## Create admin superuser
	@echo "👤 Creating superuser..."
	@cd backend && python manage.py createsuperuser

collectstatic: ## Collect static files
	@echo "📁 Collecting static files..."
	@cd backend && python manage.py collectstatic

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true 