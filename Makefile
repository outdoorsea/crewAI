# Makefile for CrewAI Agent System
# Provides convenient commands for agent development, testing, and deployment

.PHONY: help install install-dev test test-verbose test-coverage lint format type-check security-check clean build docker-build docker-run pre-commit setup-hooks git-init

# Default target
help:
	@echo "🤖 CrewAI Agent System - Multi-Agent Orchestration Platform"
	@echo "=========================================================="
	@echo ""
	@echo "Development Commands:"
	@echo "  setup          - Initial project setup (install + hooks + git)"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  setup-hooks    - Setup git pre-commit hooks"
	@echo ""
	@echo "Code Quality:"
	@echo "  format         - Format code with Ruff"
	@echo "  lint           - Run all linters (ruff + mypy + bandit)"
	@echo "  type-check     - Run mypy type checking"
	@echo "  security-check - Run bandit security analysis"
	@echo "  pre-commit     - Run all pre-commit hooks"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-verbose   - Run tests with verbose output"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-agents    - Test agent functionality specifically"
	@echo "  test-tools     - Test HTTP tool bridge"
	@echo ""
	@echo "Application:"
	@echo "  run-server     - Start OpenWebUI pipeline server"
	@echo "  run-agents     - Run agent demonstration"
	@echo "  validate       - Validate agent configurations"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run in Docker container"
	@echo ""
	@echo "Git & Deployment:"
	@echo "  git-init       - Initialize git repository with best practices"
	@echo "  clean          - Clean build artifacts"
	@echo "  build          - Build distribution packages"

# Project Setup
setup: install-dev setup-hooks git-init
	@echo "✅ CrewAI project setup complete!"

install:
	python -m pip install -e .

install-dev:
	python -m pip install -e ".[dev]"
	python -m pip install pre-commit ruff mypy bandit pytest pytest-asyncio

setup-hooks:
	pre-commit install
	pre-commit install --hook-type commit-msg

# Code Quality
format:
	@echo "🎨 Formatting code..."
	ruff format .
	@echo "✅ Code formatted"

lint: format type-check security-check
	@echo "🔍 Running linters..."
	ruff check . --fix
	@echo "✅ Linting complete"

type-check:
	@echo "🔍 Type checking..."
	mypy --ignore-missing-imports --check-untyped-defs .
	@echo "✅ Type checking complete"

security-check:
	@echo "🔒 Security analysis..."
	bandit -r . -x tests/,venv/,env/,build/,dist/,memory_data/,logs/
	@echo "✅ Security check complete"

pre-commit:
	@echo "🚀 Running pre-commit hooks..."
	pre-commit run --all-files
	@echo "✅ Pre-commit hooks complete"

# Testing
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v
	@echo "✅ Tests complete"

test-verbose:
	@echo "🧪 Running tests (verbose)..."
	python -m pytest tests/ -v -s
	@echo "✅ Verbose tests complete"

test-coverage:
	@echo "🧪 Running tests with coverage..."
	python -m pytest --cov=. --cov-report=term-missing tests/
	@echo "✅ Coverage tests complete"

test-agents:
	@echo "🤖 Testing agent functionality..."
	python -m pytest tests/test_agents.py -v
	python -m pytest tests/test_fastapi_*_agent.py -v
	@echo "✅ Agent tests complete"

test-tools:
	@echo "🔧 Testing HTTP tool bridge..."
	python -m pytest tests/test_tool_bridge.py -v
	python -m pytest tests/test_http_client_tools.py -v
	@echo "✅ Tool tests complete"

# Application
run-server:
	@echo "🚀 Starting OpenWebUI pipeline server..."
	python pipeline/server.py

run-agents:
	@echo "🤖 Running agent demonstration..."
	@python -c "\
from agents.agent_manager import get_available_agents; \
agents = get_available_agents(); \
print(f'Available agents: {list(agents.keys())}')"

validate:
	@echo "✅ Validating agent configurations..."
	@python -c "\
from agents.agent_manager import get_available_agents; \
agents = get_available_agents(); \
print(f'✅ {len(agents)} agents configured successfully')"

# Docker
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t crewai-agents:latest .
	@echo "✅ Docker image built"

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 9091:9091 crewai-agents:latest
	@echo "✅ Docker container started"

# Git and Repository Management  
git-init:
	@echo "🔧 Initializing git repository..."
	@if [ ! -d .git ]; then \
		git init; \
		echo "📁 Git repository initialized"; \
	else \
		echo "📁 Git repository already exists"; \
	fi
	@echo "🔧 Setting up .gitignore..."
	@if [ ! -f .gitignore ]; then \
		echo "# CrewAI Agent System .gitignore" > .gitignore; \
		echo "" >> .gitignore; \
		echo "# Python" >> .gitignore; \
		echo "__pycache__/" >> .gitignore; \
		echo "*.py[cod]" >> .gitignore; \
		echo "*$py.class" >> .gitignore; \
		echo "*.so" >> .gitignore; \
		echo ".Python" >> .gitignore; \
		echo "build/" >> .gitignore; \
		echo "develop-eggs/" >> .gitignore; \
		echo "dist/" >> .gitignore; \
		echo "downloads/" >> .gitignore; \
		echo "eggs/" >> .gitignore; \
		echo ".eggs/" >> .gitignore; \
		echo "lib/" >> .gitignore; \
		echo "lib64/" >> .gitignore; \
		echo "parts/" >> .gitignore; \
		echo "sdist/" >> .gitignore; \
		echo "var/" >> .gitignore; \
		echo "wheels/" >> .gitignore; \
		echo "*.egg-info/" >> .gitignore; \
		echo ".installed.cfg" >> .gitignore; \
		echo "*.egg" >> .gitignore; \
		echo "MANIFEST" >> .gitignore; \
		echo "" >> .gitignore; \
		echo "# Virtual Environment" >> .gitignore; \
		echo "venv/" >> .gitignore; \
		echo "env/" >> .gitignore; \
		echo "ENV/" >> .gitignore; \
		echo "env.bak/" >> .gitignore; \
		echo "venv.bak/" >> .gitignore; \
		echo "" >> .gitignore; \
		echo "# IDE" >> .gitignore; \
		echo ".vscode/" >> .gitignore; \
		echo ".idea/" >> .gitignore; \
		echo "*.swp" >> .gitignore; \
		echo "*.swo" >> .gitignore; \
		echo "*~" >> .gitignore; \
		echo "" >> .gitignore; \
		echo "# OS" >> .gitignore; \
		echo ".DS_Store" >> .gitignore; \
		echo ".DS_Store?" >> .gitignore; \
		echo "._*" >> .gitignore; \
		echo ".Spotlight-V100" >> .gitignore; \
		echo ".Trashes" >> .gitignore; \
		echo "ehthumbs.db" >> .gitignore; \
		echo "Thumbs.db" >> .gitignore; \
		echo "" >> .gitignore; \
		echo "# Logs and Databases" >> .gitignore; \
		echo "logs/" >> .gitignore; \
		echo "*.log" >> .gitignore; \
		echo "*.db" >> .gitignore; \
		echo "*.sqlite" >> .gitignore; \
		echo "" >> .gitignore; \
		echo "# Configuration and Secrets" >> .gitignore; \
		echo ".env" >> .gitignore; \
		echo "secrets/" >> .gitignore; \
		echo "" >> .gitignore; \
		echo "# Testing and Coverage" >> .gitignore; \
		echo ".pytest_cache/" >> .gitignore; \
		echo ".coverage" >> .gitignore; \
		echo "htmlcov/" >> .gitignore; \
		echo ".tox/" >> .gitignore; \
		echo "" >> .gitignore; \
		echo "# Agent Memory Data" >> .gitignore; \
		echo "memory_data/" >> .gitignore; \
		echo "*.json.bak" >> .gitignore; \
		echo "" >> .gitignore; \
		echo "# OpenWebUI Pipeline Data" >> .gitignore; \
		echo "pipeline/memory_data/" >> .gitignore; \
		echo "📁 .gitignore created"; \
	else \
		echo "📁 .gitignore already exists"; \
	fi
	@echo "✅ Git setup complete"

# Cleanup and Build
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

build: clean lint test
	@echo "📦 Building distribution packages..."
	python -m build
	@echo "✅ Build complete"

# Development workflow
dev-setup: install-dev setup-hooks
	@echo "🚀 Development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  make test          # Run tests"
	@echo "  make run-server    # Start pipeline server"
	@echo "  make run-agents    # Test agent functionality"
	@echo ""

# CI/CD helpers
ci-test: install-dev lint test-coverage
	@echo "✅ CI tests complete"

ci-build: ci-test build
	@echo "✅ CI build complete"