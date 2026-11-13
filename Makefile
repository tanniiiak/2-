.PHONY: run test lint

run:
	python -m src.main --config config.example.toml

test:
	python -m pytest -q

lint:
	python -m ruff check src tests