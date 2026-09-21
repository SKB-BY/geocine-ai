.PHONY: up down logs seed api fmt

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

fmt:
	cd backend && python -m ruff check --fix . || true
