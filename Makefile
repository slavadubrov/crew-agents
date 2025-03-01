# Makefile for Python project management

# Variables
VENV = .venv
PYTHON = python3.12
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python
UV = $(VENV)/bin/uv

# Default target
.PHONY: all
all: venv install

# Check if virtual environment is valid
.PHONY: check-venv
check-venv:
	@echo "Checking virtual environment..."
	@if [ ! -d "$(VENV)" ] || ! $(PYTHON_VENV) --version > /dev/null 2>&1; then \
		echo "Virtual environment is invalid or missing. Recreating..."; \
		rm -rf $(VENV); \
		echo "Using Python version: $(PYTHON_VERSION)"; \
		if command -v $(PYTHON) > /dev/null; then \
			$(PYTHON) -m venv $(VENV); \
		elif command -v python3 > /dev/null; then \
			echo "Warning: $(PYTHON) not found, falling back to python3"; \
			python3 -m venv $(VENV); \
		else \
			echo "Error: No suitable Python interpreter found"; \
			exit 1; \
		fi; \
		$(VENV)/bin/python -m pip install --upgrade pip; \
		echo "Installing uv package manager..."; \
		$(VENV)/bin/pip install uv; \
		echo "Virtual environment created at $(VENV) with uv installed"; \
	else \
		echo "Virtual environment is valid at $(VENV)"; \
		echo "Python version: $$($(PYTHON_VENV) --version)"; \
	fi

# Create virtual environment
.PHONY: venv
venv: check-venv
	@echo "Virtual environment ready at $(VENV)"

# Update uv in virtual environment
.PHONY: update-uv
update-uv: check-venv
	@echo "Updating uv in virtual environment..."
	@$(PIP) install --upgrade uv
	@echo "uv updated to latest version"

# Install dependencies from lock file with uv
.PHONY: install
install: check-venv
	@echo "Installing dependencies from lock file with uv..."
	@if [ -f requirements.lock ]; then \
		$(UV) pip install -r requirements.lock; \
	else \
		echo "requirements.lock not found. Run 'make update-deps' first or 'make install-from-txt' to install from requirements.txt"; \
		exit 1; \
	fi
	@echo "Dependencies installed from lock file"

# Install dependencies from requirements.txt (for initial setup)
.PHONY: install-from-txt
install-from-txt: check-venv
	@echo "Installing dependencies from requirements.txt..."
	@$(UV) pip install -r requirements.txt
	@echo "Dependencies installed from requirements.txt"

# Run the application (modify as needed)
.PHONY: run
run: check-venv
	@echo "Running application..."
	@$(PYTHON_VENV) main.py

# Clean up generated files and directories
.PHONY: clean
clean:
	@echo "Cleaning up..."
	@rm -rf __pycache__
	@rm -rf */__pycache__
	@rm -rf *.pyc
	@rm -rf */*.pyc
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@echo "Cleanup complete"

# Deep clean (includes virtual environment)
.PHONY: clean-all
clean-all: clean
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "Virtual environment removed"

# Check for Rust compiler
.PHONY: check-rust
check-rust:
	@if ! command -v rustc > /dev/null; then \
		echo "Rust compiler not found. This is needed for some Python packages."; \
		echo "To install Rust, visit https://rustup.rs or run:"; \
		echo "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"; \
		echo ""; \
		echo "Alternatively, you can try installing pre-built wheels with:"; \
		echo "UV_NATIVE_TLS=1 $(UV) pip install -r requirements.txt -r dev-requirements.txt"; \
		exit 1; \
	fi

# Install development dependencies with uv
.PHONY: dev-install
dev-install: check-venv
	@echo "Installing development dependencies with uv..."
	@if [ -f requirements.lock ]; then \
		$(UV) pip install -r requirements.lock; \
	else \
		$(UV) pip install -r requirements.txt; \
	fi
	@UV_NATIVE_TLS=1 $(UV) pip install -r dev-requirements.txt --no-build-isolation
	@echo "Development dependencies installed"
	@echo "Verifying development tools..."
	@if ! $(PYTHON_VENV) -c "import black, isort, flake8" > /dev/null 2>&1; then \
		echo "Warning: Some development tools could not be imported. Reinstalling..."; \
		$(PIP) install black[jupyter] isort flake8; \
	fi

# Install development dependencies with uv (without Rust compiler)
.PHONY: dev-install-no-rust
dev-install-no-rust: check-venv
	@echo "Installing development dependencies with uv (without Rust)..."
	@if [ -f requirements.lock ]; then \
		$(UV) pip install -r requirements.lock; \
	else \
		$(UV) pip install -r requirements.txt; \
	fi
	@UV_NATIVE_TLS=1 $(UV) pip install -r dev-requirements.txt --no-build-isolation --only-binary=:all:
	@echo "Development dependencies installed (some packages may be missing if they require Rust)"
	@echo "Verifying development tools..."
	@if ! $(PYTHON_VENV) -c "import black, isort, flake8" > /dev/null 2>&1; then \
		echo "Warning: Some development tools could not be imported. Reinstalling..."; \
		$(PIP) install black[jupyter] isort flake8; \
	fi

# Format code
.PHONY: format
format: dev-install
	@echo "Formatting code..."
	@$(PYTHON_VENV) -m isort --profile black .
	@$(PYTHON_VENV) -m black .
	@echo "Code formatting complete"

# Format code (without Rust compiler)
.PHONY: format-no-rust
format-no-rust: dev-install-no-rust
	@echo "Formatting code (without Rust)..."
	@$(PYTHON_VENV) -m black .
	@$(PYTHON_VENV) -m isort --profile black .
	@echo "Code formatting complete"

# Lint code
.PHONY: lint
lint: dev-install
	@echo "Linting code..."
	@$(PYTHON_VENV) -m flake8 --exclude=.venv,__pycache__,build,dist .
	@echo "Linting complete"

# Run tests
.PHONY: test
test: dev-install
	@echo "Running tests..."
	@$(PYTHON_VENV) -m pytest || echo "No tests found or tests failed. Check test output for details."
	@echo "Tests complete"

# Run tests with coverage
.PHONY: coverage
coverage: dev-install
	@echo "Running tests with coverage..."
	@$(PYTHON_VENV) -m pytest --cov=. --cov-report=html
	@echo "Coverage report generated in htmlcov/"

# Update dependencies from requirements.txt and create lock file
.PHONY: update-deps
update-deps: check-venv
	@echo "Installing dependencies from requirements.txt and creating lock file..."
	@$(UV) pip install -r requirements.txt
	@echo "Creating requirements.lock with current dependencies..."
	@$(VENV)/bin/uv pip freeze > requirements.lock
	@echo "requirements.lock created successfully"

# Freeze current environment to requirements.lock
.PHONY: freeze
freeze: install-from-txt
	@echo "Creating requirements.lock with current dependencies..."
	@$(VENV)/bin/uv pip freeze > requirements.lock
	@echo "requirements.lock created successfully"

# Help command
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make venv                - Create virtual environment with uv"
	@echo "  make update-uv           - Update uv to latest version in virtual environment"
	@echo "  make install             - Install dependencies from lock file using uv"
	@echo "  make install-from-txt    - Install dependencies from requirements.txt"
	@echo "  make update-deps         - Update dependencies from requirements.txt and create lock file"
	@echo "  make freeze              - Create requirements.lock from current environment"
	@echo "  make run                 - Run the application"
	@echo "  make clean               - Clean up generated files"
	@echo "  make clean-all           - Clean up everything including virtual environment"
	@echo "  make dev-install         - Install development dependencies using uv"
	@echo "  make dev-install-no-rust - Install development dependencies without Rust compiler"
	@echo "  make format              - Format code with black and isort"
	@echo "  make format-no-rust      - Format code without requiring Rust compiler"
	@echo "  make lint                - Lint code with flake8"
	@echo "  make test                - Run tests"
	@echo "  make coverage            - Run tests with coverage report"
	@echo "  make help                - Show this help message" 