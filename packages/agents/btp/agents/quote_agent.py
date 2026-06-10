"""QuoteAgent — analyse, quantification, chiffrage et génération de devis."""

from __future__ import annotations

from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.llm_router import LLMMessage, TaskType


class QuoteAgent(BaseAgent):
    name = "QuoteAgent"
    description = "Quantification et chiffrage : génère et révise des devis."

    async def run(self, context: AgentContext) -> AgentResult:
        client = self.router.client_for(TaskType.COMPLEX_WRITING)
        prompt = (
            "À partir de la description d'ouvrages et des quantités, produis un "
            "devis BTP structuré (lignes: désignation, unité, quantité, prix "
            f"unitaire HT). Données: {context.inputs.get('description', context.prompt)}"
        )
        response = await client.complete([LLMMessage("user", prompt)])
        return AgentResult(
            agent=self.name,
            provider=response.provider,
            summary=response.text,
            output={"devis": {"lignes": [], "total_ht": 0.0}, "raw": response.text},
        )
