.PHONY: help install install-dev test test-cov lint format clean run receiver

PYTHON := python
PYTEST := $(PYTHON) -m pytest
PIP    := $(PYTHON) -m pip

help:
	@echo "ServicesSound — available commands"
	@echo "-----------------------------------"
	@echo "  make install      Install production dependencies"
	@echo "  make install-dev  Install dev + test dependencies"
	@echo "  make run          Launch the application"
	@echo "  make test         Run test suite"
	@echo "  make test-cov     Run tests with HTML coverage report"
	@echo "  make lint         Check code style with ruff"
	@echo "  make format       Auto-format code with ruff"
	@echo "  make clean        Remove build artifacts and caches"

install:
	$(PIP) install numpy netifaces zeroconf pyyaml pyaudio

install-dev: install
	$(PIP) install pytest pytest-cov pytest-mock ruff mypy

run:
	$(PYTHON) -m src.main

receiver:
	$(PYTHON) -m receiver

test:
	$(PYTEST) test/ -v --tb=short

test-cov:
	$(PYTEST) test/ -v --tb=short \
		--cov=src --cov=config \
		--cov-report=term-missing \
		--cov-report=html:htmlcov
	@echo "Coverage report: htmlcov/index.html"

lint:
	ruff check src/ config/ test/

format:
	ruff format src/ config/ test/
	ruff check --fix src/ config/ test/

clean:
	rm -rf build/ dist/ *.egg-info/ htmlcov/
	rm -f .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
