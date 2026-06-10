"""Contrat de base des agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from btp.llm_router import LLMRouter, get_router


@dataclass
class AgentContext:
    """Contexte d'exécution passé à un agent.

    `inputs` porte les données métier (texte, références de fichiers, ids…).
    `history` permet la mémoire persistante d'une conversation.
    """

    project_id: str | None = None
    prompt: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, str]] = field(default_factory=list)


@dataclass
class AgentResult:
    agent: str
    output: dict[str, Any]
    summary: str = ""
    provider: str | None = None

    @classmethod
    def text(cls, agent: str, summary: str, **output: Any) -> AgentResult:
        return cls(agent=agent, summary=summary, output=output)


class BaseAgent(ABC):
    """Agent spécialisé. Chaque agent déclare son nom et sa mission."""

    name: str = "base"
    description: str = ""

    def __init__(self, router: LLMRouter | None = None) -> None:
        self.router = router or get_router()

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        """Exécute la tâche de l'agent et retourne un résultat structuré."""

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<{type(self).__name__} name={self.name!r}>"
