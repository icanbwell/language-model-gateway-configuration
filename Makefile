.PHONY: all clean build test lint validate docker-build docker-validate

# Variables
PYTHON := python3.12
DOCKER_IMAGE := lmg-config-validator
DOCKER_TAG := latest

# Default target
all: clean build test lint

# Clean build artifacts
clean:
	rm -rf build dist *.egg-info __pycache__ .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Build the package
build:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build

# Install in development mode
install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

# Run tests
test:
	$(PYTHON) -m pytest

# Run linting and type checking
lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy .

# Build Docker image
docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

# Validate JSON files using Docker
docker-validate:
	@if [ -z "$(FILES)" ]; then \
		echo "Usage: make docker-validate FILES='file1.json file2.json'"; \
		exit 1; \
	fi
	@mkdir -p ~/.cache/lmg-config-validator
	docker run --rm \
		-v "$(PWD):/app/data" \
		-v "$(HOME)/.cache/lmg-config-validator:/root/.cache/lmg-config-validator" \
		$(DOCKER_IMAGE):$(DOCKER_TAG) $(FILES)

# Local validation without Docker
validate:
	@if [ -z "$(FILES)" ]; then \
		echo "Usage: make validate FILES='file1.json file2.json'"; \
		exit 1; \
	fi
	validate-lmg-config $(FILES)

.PHONY:clean-pre-commit
clean-pre-commit: ## removes pre-commit hook
	rm -f .git/hooks/pre-commit

.PHONY:setup-pre-commit
setup-pre-commit:
	cp ./pre-commit-hook ./.git/hooks/pre-commit

.PHONY:run-pre-commit
run-pre-commit: setup-pre-commit
	./.git/hooks/pre-commit pre_commit_all_files
