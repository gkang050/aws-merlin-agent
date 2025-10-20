.PHONY: lint format test build-demo

setup:
	poetry install

lint:
	poetry run ruff check src tests

format:
	poetry run black src tests

test:
	poetry run pytest --cov=src --cov-report=term-missing

build-demo:
	poetry run python scripts/demo_run.py --env demo
