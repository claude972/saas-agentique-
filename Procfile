web: uv run uvicorn btp_api.main:app --host 0.0.0.0 --port ${PORT:-8000}
release: uv run alembic upgrade head
