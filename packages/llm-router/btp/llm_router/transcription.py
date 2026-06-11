"""Transcription audio (notes vocales) — Whisper / OpenAI.

Utilise le meilleur modèle de transcription disponible (Whisper d'OpenAI par
défaut, surchargeable). Sans clé `OPENAI_API_KEY`, lève `TranscriptionUnavailable`
afin que l'API renvoie un 503 explicite plutôt que d'échouer silencieusement.
"""

from __future__ import annotations

import io
import os

DEFAULT_MODEL = "whisper-1"


class TranscriptionUnavailable(RuntimeError):
    """Aucun fournisseur de transcription n'est configuré."""


def transcription_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


async def transcribe(audio: bytes, *, filename: str = "audio.webm") -> str:
    """Transcrit un enregistrement audio en texte.

    `audio` : octets bruts (webm/mp3/wav/m4a…). Retourne le texte transcrit.
    """
    if not transcription_available():
        raise TranscriptionUnavailable(
            "OPENAI_API_KEY requis pour la transcription (Whisper)."
        )

    from openai import AsyncOpenAI  # import paresseux (offline-safe)

    client = AsyncOpenAI()
    model = os.getenv("OPENAI_TRANSCRIBE_MODEL", DEFAULT_MODEL)
    buffer = io.BytesIO(audio)
    buffer.name = filename  # le SDK déduit le type depuis l'extension
    result = await client.audio.transcriptions.create(model=model, file=buffer)
    return result.text
