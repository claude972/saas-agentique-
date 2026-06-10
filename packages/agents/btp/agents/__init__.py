"""Architecture agentique — BTP Agent Platform."""

from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.agents.consultation_agent import ConsultationAgent
from btp.agents.document_agent import DocumentAgent
from btp.agents.photo_agent import PhotoAgent
from btp.agents.quote_agent import QuoteAgent
from btp.agents.registry import AGENT_REGISTRY, get_agent, list_agents
from btp.agents.report_agent import ReportAgent
from btp.agents.supervisor import SupervisorAgent
from btp.agents.tender_agent import TenderAgent

__all__ = [
    "BaseAgent",
    "AgentContext",
    "AgentResult",
    "SupervisorAgent",
    "PhotoAgent",
    "QuoteAgent",
    "ConsultationAgent",
    "TenderAgent",
    "ReportAgent",
    "DocumentAgent",
    "AGENT_REGISTRY",
    "get_agent",
    "list_agents",
]
