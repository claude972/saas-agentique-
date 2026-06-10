"""Point d'entrée de l'API FastAPI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from btp_api.config import get_settings
from btp_api.routers import (
    agents,
    auth,
    chat,
    documents,
    health,
    projects,
    quotes,
    users,
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Plateforme agentique SaaS spécialisée BTP.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(projects.router)
    app.include_router(documents.router)
    app.include_router(quotes.router)
    app.include_router(chat.router)
    app.include_router(agents.router)

    @app.get("/", tags=["health"])
    def root() -> dict[str, str]:
        return {"name": settings.app_name, "docs": "/docs"}

    return app


app = create_app()
