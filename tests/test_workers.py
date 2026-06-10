"""Tests de la file de tâches (repli synchrone hors Redis)."""

from __future__ import annotations

import pytest
from btp_workers import enqueue, redis_available, run_sync


def test_enqueue_runs_inline_without_redis(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    assert redis_available() is False

    job = enqueue("supervisor.run", prompt="Rédige un compte-rendu de réunion")
    assert job["status"] == "finished"
    assert job["backend"] == "inline"
    assert job["result"]["plan"]["agents"] == ["ReportAgent"]


def test_unknown_task_raises():
    with pytest.raises(KeyError):
        run_sync("does.not.exist")
    with pytest.raises(KeyError):
        enqueue("does.not.exist")
