"""Recherche sémantique / RAG — BTP Agent Platform.

Index en mémoire par défaut (dev/tests). En production, à remplacer par
pgvector / Qdrant en conservant l'interface `VectorStore`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from btp.llm_router import EchoProvider, LLMProvider

__all__ = ["VectorStore", "SearchHit", "InMemoryVectorStore"]


@dataclass
class SearchHit:
    doc_id: str
    score: float
    text: str


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class VectorStore:
    """Interface de magasin vectoriel."""

    async def index(self, doc_id: str, text: str) -> None:  # pragma: no cover
        raise NotImplementedError

    async def search(self, query: str, *, top_k: int = 5) -> list[SearchHit]:  # pragma: no cover
        raise NotImplementedError


@dataclass
class InMemoryVectorStore(VectorStore):
    provider: LLMProvider = field(default_factory=EchoProvider)
    _vectors: dict[str, list[float]] = field(default_factory=dict)
    _texts: dict[str, str] = field(default_factory=dict)

    async def index(self, doc_id: str, text: str) -> None:
        (vector,) = await self.provider.embed([text])
        self._vectors[doc_id] = vector
        self._texts[doc_id] = text

    async def search(self, query: str, *, top_k: int = 5) -> list[SearchHit]:
        (qv,) = await self.provider.embed([query])
        scored = [
            SearchHit(doc_id, _cosine(qv, vec), self._texts[doc_id])
            for doc_id, vec in self._vectors.items()
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]
