"""Webhook Telegram (canal public, protégé par un secret partagé).

Telegram appelle `POST /telegram/webhook` à chaque message. La requête est
authentifiée par l'en-tête `X-Telegram-Bot-Api-Secret-Token` (et non par JWT).
Le traitement métier est délégué à `btp_telegram.handle_update`.
"""

from __future__ import annotations

from typing import Annotated, Any

from btp_telegram import handle_update
from fastapi import APIRouter, Header, HTTPException, Request, status

from btp_api.config import get_settings

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    settings = get_settings()
    secret = settings.telegram_webhook_secret
    if secret and x_telegram_bot_api_secret_token != secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Secret invalide")

    update = await request.json()
    result = await handle_update(update)
    # On répond toujours 200 rapidement (Telegram réessaie sinon).
    return {"ok": True, "handled": result.get("handled", False)}
