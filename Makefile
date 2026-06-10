.PHONY: help install api web test lint fmt up down init-db

help:
	@echo "Cibles disponibles :"
	@echo "  install   Installer les dépendances Python (uv) et JS (pnpm)"
	@echo "  up        Démarrer Postgres + Redis (docker compose)"
	@echo "  down      Arrêter l'infra locale"
	@echo "  init-db   Initialiser la base de données"
	@echo "  api       Lancer l'API FastAPI (port 8000)"
	@echo "  web       Lancer le frontend Next.js (port 3000)"
	@echo "  test      Lancer la suite de tests Python"
	@echo "  lint      Vérifier le style (ruff)"
	@echo "  fmt       Formater/corriger le code (ruff --fix)"

install:
	uv sync
	cd apps/web && pnpm install

up:
	docker compose up -d db redis

down:
	docker compose down

init-db:
	uv run btp-api init-db

api:
	uv run uvicorn btp_api.main:app --reload --port 8000

web:
	cd apps/web && pnpm dev

test:
	uv run pytest

lint:
	uv run ruff check .

fmt:
	uv run ruff check --fix .
