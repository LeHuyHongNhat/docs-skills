install:
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload --port 8000

worker:
	python -m worker.main

test:
	pytest -q
