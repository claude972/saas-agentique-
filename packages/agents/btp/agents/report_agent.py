"""ReportAgent — génération de comptes-rendus (chantier, visite, réunion, réserve)."""

from __future__ import annotations

from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.llm_router import LLMMessage, TaskType


class ReportAgent(BaseAgent):
    name = "ReportAgent"
    description = "Génère des comptes-rendus à partir de photos, audio et texte."

    async def run(self, context: AgentContext) -> AgentResult:
        client = self.router.client_for(TaskType.COMPLEX_WRITING)
        kind = context.inputs.get("kind", "chantier")
        prompt = (
            f"Rédige un compte-rendu de {kind} BTP structuré à partir des notes, "
            f"photos et audio fournis. {context.prompt}"
        )
        response = await client.complete([LLMMessage("user", prompt)])
        return AgentResult(
            agent=self.name,
            provider=response.provider,
            summary=response.text,
            output={"kind": kind, "content": response.text, "reserves": []},
        )
