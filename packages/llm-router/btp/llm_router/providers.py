"""Interface des fournisseurs LLM et implémentation mock hors-ligne.

Les intégrations réelles (Anthropic, OpenAI, Google, Mistral) implémentent la
même interface `LLMProvider`. Tant qu'aucune clé d'API n'est configurée, le
`EchoProvider` permet de développer et tester sans dépendance réseau.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)


class LLMProvider(ABC):
    """Contrat commun à tous les fournisseurs LLM."""

    name: str = "abstract"

    @abstractmethod
    async def complete(
        self, messages: list[LLMMessage], *, model: str | None = None, **kwargs: object
    ) -> LLMResponse:
        """Complétion textuelle (chat)."""

    async def vision(
        self,
        messages: list[LLMMessage],
        images: list[bytes],
        *,
        model: str | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Analyse multimodale (image + texte). Par défaut : complétion texte."""
        return await self.complete(messages, model=model, **kwargs)

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        """Vectorisation. Implémentation par défaut : non supportée."""
        raise NotImplementedError(f"{self.name} ne fournit pas d'embeddings")


class EchoProvider(LLMProvider):
    """Fournisseur mock déterministe pour dev/tests hors-ligne."""

    name = "echo"

    async def complete(
        self, messages: list[LLMMessage], *, model: str | None = None, **kwargs: object
    ) -> LLMResponse:
        last = next((m for m in reversed(messages) if m.role == "user"), None)
        prompt = last.content if last else ""
        return LLMResponse(
            text=f"[echo:{model or 'mock'}] {prompt}",
            provider=self.name,
            model=model or "mock",
            usage={"prompt_tokens": len(prompt.split()), "completion_tokens": 0},
        )

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        # Embedding déterministe minimaliste (hash → vecteur de taille fixe).
        return [[float((hash(t) >> i) & 1) for i in range(16)] for t in texts]
