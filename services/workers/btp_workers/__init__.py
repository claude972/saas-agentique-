"""Workers asynchrones — BTP Agent Platform.

Exécute les tâches longues (analyse photo, génération de devis, crawl AO…)
hors du cycle requête/réponse de l'API. L'orchestration métier est déléguée
au `SupervisorAgent` ; ce module ne porte que la mécanique de file de tâches.
"""

from __future__ import annotations

import asyncio
import os
import uuid
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
    if name not in TASKS:
        raise KeyError(f"Tâche inconnue: {name!r}")
    return asyncio.run(TASKS[name](**kwargs))


def redis_available() -> bool:
    """Vrai si Redis et RQ sont disponibles et joignables."""
    url = os.getenv("REDIS_URL")
    if not url:
        return False
    try:
        import redis  # import paresseux
        import rq  # noqa: F401

        redis.from_url(url, socket_connect_timeout=1).ping()
        return True
    except Exception:
        return False


def enqueue(name: str, /, **kwargs: Any) -> dict[str, Any]:
    """Soumet une tâche à la file.

    Avec Redis/RQ disponibles → mise en file asynchrone (`queued`). Sinon, repli
    synchrone immédiat (`finished` + `result`) : la plateforme reste fonctionnelle
    sans infrastructure, et l'API peut basculer en asynchrone sans changer d'appel.
    """
    if name not in TASKS:
        raise KeyError(f"Tâche inconnue: {name!r}")

    if redis_available():
        import redis
        from rq import Queue

        queue = Queue("btp", connection=redis.from_url(os.environ["REDIS_URL"]))
        job = queue.enqueue("btp_workers.runner.run", name, kwargs)
        return {"id": job.id, "status": "queued", "backend": "redis"}

    result = run_sync(name, **kwargs)
    return {"id": str(uuid.uuid4()), "status": "finished", "backend": "inline", "result": result}
