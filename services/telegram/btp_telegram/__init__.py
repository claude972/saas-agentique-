"""Bot Telegram — BTP Agent Platform.

Deux directions :
- **entrant** : `handle_update` route les messages Telegram (texte, photo, voix)
  vers les agents (Supervisor / PhotoAgent / transcription) et répond.
- **sortant** : `notify` pousse des messages (ex. AO détecté GO) vers un chat.

Le token n'est requis que pour les appels réseau réels ; sans token, les envois
sont des no-op et le routage reste testable hors-ligne.
"""

from __future__ import annotations

import os
from typing import Any

from btp.agents import AgentContext, SupervisorAgent, get_agent
from btp.llm_router import TranscriptionUnavailable, transcribe

API_BASE = "https://api.telegram.org"

_WELCOME = (
    "👷 *BTP Agent Platform*\n"
    "Envoyez :\n"
    "• un *message* → un agent vous répond ;\n"
    "• une *photo* de chantier → analyse (ouvrages, anomalies) ;\n"
    "• un *message vocal* → transcription + compte-rendu.\n"
)


def configured() -> bool:
    return bool(os.getenv("TELEGRAM_BOT_TOKEN"))


def _token() -> str:
    return os.environ["TELEGRAM_BOT_TOKEN"]


async def send_message(chat_id: int | str, text: str) -> dict[str, Any]:
    """Envoie un message texte (Markdown). No-op si le bot n'est pas configuré."""
    if not configured():
        return {"skipped": "no_token"}
    import httpx

    async with httpx.AsyncClient(timeout=15.0) as http:
        resp = await http.post(
            f"{API_BASE}/bot{_token()}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        )
        return resp.json()


async def _download(file_id: str) -> bytes | None:
    """Télécharge le contenu d'un fichier Telegram (photo, voix). Token requis."""
    if not configured():
        return None
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as http:
        meta = await http.get(f"{API_BASE}/bot{_token()}/getFile", params={"file_id": file_id})
        path = meta.json().get("result", {}).get("file_path")
        if not path:
            return None
        data = await http.get(f"{API_BASE}/file/bot{_token()}/{path}")
        return data.content


async def notify(text: str, *, chat_id: int | str | None = None) -> dict[str, Any]:
    """Notification sortante vers un chat (par défaut `TELEGRAM_ALERT_CHAT_ID`)."""
    target = chat_id or os.getenv("TELEGRAM_ALERT_CHAT_ID")
    if not target:
        return {"skipped": "no_chat"}
    return await send_message(target, text)


async def _reply_for(message: dict[str, Any]) -> str:
    """Calcule la réponse de l'agent en fonction du type de message reçu."""
    text = message.get("text", "")

    if text.startswith("/start") or text.startswith("/help"):
        return _WELCOME

    if "photo" in message:
        # La plus grande résolution est la dernière de la liste.
        photo = message["photo"][-1]
        data = await _download(photo["file_id"])
        if data is None:
            return "📷 Photo reçue, mais le bot n'est pas configuré pour l'analyser."
        result = await get_agent("PhotoAgent").run(
            AgentContext(prompt=message.get("caption", ""), inputs={"images": [data]})
        )
        return f"📷 *Analyse photo*\n{result.summary}"

    if "voice" in message or "audio" in message:
        blob = message.get("voice") or message.get("audio")
        data = await _download(blob["file_id"])
        if data is None:
            return "🎙️ Message vocal reçu, mais le bot n'est pas configuré pour le transcrire."
        try:
            transcript = await transcribe(data, filename="voice.ogg")
        except TranscriptionUnavailable:
            return "🎙️ Transcription indisponible (clé OpenAI requise)."
        result = await SupervisorAgent().run(AgentContext(prompt=transcript))
        return f"🎙️ _{transcript}_\n\n{result['summary']}"

    if text:
        result = await SupervisorAgent().run(AgentContext(prompt=text))
        return str(result["summary"]) or "Je n'ai pas pu produire de réponse."

    return "Type de message non géré. Envoyez un texte, une photo ou un vocal."


async def handle_update(update: dict[str, Any]) -> dict[str, Any]:
    """Traite une mise à jour Telegram et envoie la réponse. Retourne un résumé."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return {"handled": False, "reason": "no_message"}

    chat_id = message.get("chat", {}).get("id")
    reply = await _reply_for(message)
    send_result = await send_message(chat_id, reply) if chat_id is not None else {}
    return {"handled": True, "chat_id": chat_id, "reply": reply, "send": send_result}


async def set_webhook(url: str, *, secret: str | None = None) -> dict[str, Any]:
    """Enregistre l'URL de webhook auprès de Telegram (token requis)."""
    if not configured():
        raise RuntimeError("TELEGRAM_BOT_TOKEN requis pour configurer le webhook.")
    import httpx

    payload: dict[str, Any] = {"url": url}
    if secret:
        payload["secret_token"] = secret
    async with httpx.AsyncClient(timeout=15.0) as http:
        resp = await http.post(f"{API_BASE}/bot{_token()}/setWebhook", json=payload)
        return resp.json()
