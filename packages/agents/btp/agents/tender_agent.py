"""TenderAgent — rédaction de la réponse à appel d'offres.

Mémoire technique, planning, méthodologie, organisation chantier.
Routage : rédaction complexe / AO → Claude (cf. SRS).
"""

from __future__ import annotations

from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.llm_router import LLMMessage, TaskType


class TenderAgent(BaseAgent):
    name = "TenderAgent"
    description = "Rédige mémoire technique, planning, méthodologie et organisation chantier."

    async def run(self, context: AgentContext) -> AgentResult:
        client = self.router.client_for(TaskType.TENDER)
        prompt = (
            "Rédige une réponse à appel d'offres BTP : mémoire technique, "
            "planning prévisionnel, méthodologie et organisation de chantier, "
            f"à partir de l'analyse de consultation. {context.prompt}"
        )
        response = await client.complete([LLMMessage("user", prompt)])
        return AgentResult(
            agent=self.name,
            provider=response.provider,
            summary=response.text,
            output={
                "memoire_technique": response.text,
                "planning": None,
                "methodologie": None,
                "organisation": None,
            },
        )
