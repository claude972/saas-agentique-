"""Registre des agents spécialisés disponibles pour le Supervisor."""

from __future__ import annotations

from btp.agents.base import BaseAgent
from btp.agents.consultation_agent import ConsultationAgent
from btp.agents.document_agent import DocumentAgent
from btp.agents.photo_agent import PhotoAgent
from btp.agents.quote_agent import QuoteAgent
from btp.agents.report_agent import ReportAgent
from btp.agents.tender_agent import TenderAgent

# Classes d'agents indexées par nom canonique.
AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    PhotoAgent.name: PhotoAgent,
    QuoteAgent.name: QuoteAgent,
    ConsultationAgent.name: ConsultationAgent,
    TenderAgent.name: TenderAgent,
    ReportAgent.name: ReportAgent,
    DocumentAgent.name: DocumentAgent,
}


def get_agent(name: str) -> BaseAgent:
    try:
        return AGENT_REGISTRY[name]()
    except KeyError as exc:
        raise KeyError(f"Agent inconnu: {name!r}") from exc


def list_agents() -> list[dict[str, str]]:
    return [
        {"name": cls.name, "description": cls.description}
        for cls in AGENT_REGISTRY.values()
    ]
