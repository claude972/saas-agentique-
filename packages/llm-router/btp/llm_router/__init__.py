"""Routage multi-LLM — BTP Agent Platform.

Sélectionne le fournisseur (Claude / GPT / Gemini / Mistral) le plus adapté
selon la nature de la tâche, conformément au SRS :

- Claude  : AO, mémoire technique, rédaction complexe
- GPT     : vision, OCR, analyse photo
- Gemini  : gros PDF, recherche documentaire
- Mistral : classification, extraction simple
"""

from btp.llm_router.providers import (
    EchoProvider,
    LLMMessage,
    LLMProvider,
    LLMResponse,
)
from btp.llm_router.router import (
    DEFAULT_ROUTING,
    LLMRouter,
    Provider,
    TaskType,
    get_router,
)
from btp.llm_router.transcription import (
    TranscriptionUnavailable,
    transcribe,
    transcription_available,
)

__all__ = [
    "LLMRouter",
    "get_router",
    "Provider",
    "TaskType",
    "DEFAULT_ROUTING",
    "LLMProvider",
    "LLMMessage",
    "LLMResponse",
    "EchoProvider",
    "transcribe",
    "transcription_available",
    "TranscriptionUnavailable",
]
