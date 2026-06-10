"""Table de routage tâche → fournisseur LLM."""

from __future__ import annotations

import enum
import os
from functools import lru_cache

from btp.llm_router.providers import EchoProvider, LLMProvider


class Provider(str, enum.Enum):
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    MISTRAL = "mistral"


class TaskType(str, enum.Enum):
    # → Claude
    TENDER = "tender"
    TECHNICAL_MEMO = "technical_memo"
    COMPLEX_WRITING = "complex_writing"
    # → GPT
    VISION = "vision"
    OCR_PHOTO = "ocr_photo"
    PHOTO_ANALYSIS = "photo_analysis"
    # → Gemini
    LARGE_PDF = "large_pdf"
    DOC_SEARCH = "doc_search"
    # → Mistral
    CLASSIFICATION = "classification"
    SIMPLE_EXTRACTION = "simple_extraction"


DEFAULT_ROUTING: dict[TaskType, Provider] = {
    TaskType.TENDER: Provider.CLAUDE,
    TaskType.TECHNICAL_MEMO: Provider.CLAUDE,
    TaskType.COMPLEX_WRITING: Provider.CLAUDE,
    TaskType.VISION: Provider.GPT,
    TaskType.OCR_PHOTO: Provider.GPT,
    TaskType.PHOTO_ANALYSIS: Provider.GPT,
    TaskType.LARGE_PDF: Provider.GEMINI,
    TaskType.DOC_SEARCH: Provider.GEMINI,
    TaskType.CLASSIFICATION: Provider.MISTRAL,
    TaskType.SIMPLE_EXTRACTION: Provider.MISTRAL,
}

# Clé d'environnement attendue par fournisseur (présence → intégration réelle).
_PROVIDER_ENV_KEY: dict[Provider, str] = {
    Provider.CLAUDE: "ANTHROPIC_API_KEY",
    Provider.GPT: "OPENAI_API_KEY",
    Provider.GEMINI: "GOOGLE_API_KEY",
    Provider.MISTRAL: "MISTRAL_API_KEY",
}


class LLMRouter:
    """Achemine une `TaskType` vers le `Provider` adéquat et son client.

    La table de routage est surchargeable. Tant que la clé d'API d'un
    fournisseur n'est pas configurée, un `EchoProvider` est renvoyé afin de
    permettre le développement hors-ligne.
    """

    def __init__(self, routing: dict[TaskType, Provider] | None = None) -> None:
        self._routing = {**DEFAULT_ROUTING, **(routing or {})}
        self._clients: dict[Provider, LLMProvider] = {}

    def route(self, task: TaskType) -> Provider:
        return self._routing[task]

    def is_configured(self, provider: Provider) -> bool:
        return bool(os.getenv(_PROVIDER_ENV_KEY[provider]))

    def client_for(self, task: TaskType) -> LLMProvider:
        provider = self.route(task)
        if provider not in self._clients:
            self._clients[provider] = self._build_client(provider)
        return self._clients[provider]

    def _build_client(self, provider: Provider) -> LLMProvider:
        """Construit le client d'un provider.

        Stratégie pour rester fonctionnel dès qu'une seule clé est fournie :
        1. si le provider routé est configuré → son client réel ;
        2. sinon, si Claude est configuré → Claude (multimodal, polyvalent) ;
        3. sinon → mock déterministe hors-ligne.
        """
        if self.is_configured(provider):
            return self._make_real(provider)
        if self.is_configured(Provider.CLAUDE):
            return self._make_real(Provider.CLAUDE)
        return EchoProvider()

    def _make_real(self, provider: Provider) -> LLMProvider:
        if provider is Provider.CLAUDE:
            from btp.llm_router.anthropic_provider import AnthropicProvider

            return AnthropicProvider()
        # Les intégrations GPT / Gemini / Mistral seront branchées ici ;
        # en attendant, on retombe sur Claude si possible, sinon sur le mock.
        if self.is_configured(Provider.CLAUDE):
            from btp.llm_router.anthropic_provider import AnthropicProvider

            return AnthropicProvider()
        return EchoProvider()


@lru_cache(maxsize=1)
def get_router() -> LLMRouter:
    return LLMRouter()
