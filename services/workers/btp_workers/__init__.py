"""Workers asynchrones — BTP Agent Platform.

Exécute les tâches longues (analyse photo, génération de devis, crawl AO…)
hors du cycle requête/réponse de l'API. L'orchestration métier est déléguée
au `SupervisorAgent` ; ce module ne porte que la mécanique de file de tâches.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from btp.agents import AgentContext, SupervisorAgent

# Registre de tâches enregistrables (nom → coroutine).
TASKS: dict[str, Callable[..., Awaitable[Any]]] = {}


def task(name: str) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    def decorator(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        TASKS[name] = fn
        return fn

    return decorator


@task("supervisor.run")
async def run_supervisor_task(prompt: str, project_id: str | None = None, **inputs: Any) -> Any:
    supervisor = SupervisorAgent()
    return await supervisor.run(
        AgentContext(project_id=project_id, prompt=prompt, inputs=inputs)
    )


def run_sync(name: str, /, **kwargs: Any) -> Any:
    """Exécute une tâche de façon synchrone (utile pour les tests/CLI)."""
    return asyncio.run(TASKS[name](**kwargs))
