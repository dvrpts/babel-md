.PHONY: init dev lint format test docker-build docker-run

init:
	uv sync --all-extras

dev:
	uv run uvicorn babel_md.main:app --reload --host 0.0.0.0 --port 8000

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

test:
	uv run pytest -v

docker-build:
	docker build -t babel-md .

docker-run:
	docker run --rm -p 8000:8000 -e GEMINI_API_KEY=$(GEMINI_API_KEY) babel-md
