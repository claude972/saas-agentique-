"""Tests du bot Telegram (hors-ligne : token absent → envois no-op)."""

from __future__ import annotations

import pytest
from btp_telegram import configured, handle_update, notify


@pytest.fixture()
def no_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_ALERT_CHAT_ID", raising=False)
    return monkeypatch


async def test_handle_text_routes_to_agent(no_token):
    assert configured() is False
    update = {
        "message": {
            "chat": {"id": 4242},
            "text": "Rédige un compte-rendu de réunion",
        }
    }
    result = await handle_update(update)
    assert result["handled"] is True
    assert result["chat_id"] == 4242
    # Le SupervisorAgent route vers ReportAgent → présent dans la réponse.
    assert "ReportAgent" in result["reply"]
    assert result["send"] == {"skipped": "no_token"}


async def test_handle_start_command(no_token):
    update = {"message": {"chat": {"id": 1}, "text": "/start"}}
    result = await handle_update(update)
    assert "BTP Agent Platform" in result["reply"]


async def test_notify_noop_without_chat(no_token):
    assert await notify("coucou") == {"skipped": "no_chat"}


async def test_webhook_endpoint_and_secret(client, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    # Sans secret configuré, le webhook accepte la requête.
    resp = client.post(
        "/telegram/webhook",
        json={"message": {"chat": {"id": 7}, "text": "bonjour"}},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_webhook_rejects_bad_secret(client, monkeypatch):
    from btp_api.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "topsecret")
    try:
        resp = client.post(
            "/telegram/webhook",
            json={"message": {"chat": {"id": 7}, "text": "x"}},
            headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
        )
        assert resp.status_code == 403
    finally:
        get_settings.cache_clear()
