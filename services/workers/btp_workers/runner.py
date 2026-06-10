"""Point d'exécution des tâches côté worker RQ.

Lancement d'un worker :  uv run rq worker btp
La fonction `run` est référencée par `btp_workers.enqueue` lors de la mise en file.
"""

from __future__ import annotations

from typing import Any

from btp_workers import run_sync


def run(name: str, kwargs: dict[str, Any]) -> Any:
    """Exécute la tâche enregistrée `name` avec ses arguments (appelé par RQ)."""
    return run_sync(name, **kwargs)
