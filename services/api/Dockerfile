# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# uv pour la résolution du workspace
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./
COPY packages ./packages
COPY services ./services

RUN uv sync --frozen --no-dev || uv sync --no-dev

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "btp_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
