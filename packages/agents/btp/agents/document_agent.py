"""DocumentAgent — classement, OCR, recherche documentaire et extraction."""

from __future__ import annotations

from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.llm_router import LLMMessage, TaskType


class DocumentAgent(BaseAgent):
    name = "DocumentAgent"
    description = "Classe, OCR-ise, indexe et extrait des données des documents."

    async def run(self, context: AgentContext) -> AgentResult:
        # Classification / extraction simple → Mistral (cf. SRS).
        client = self.router.client_for(TaskType.CLASSIFICATION)
        prompt = (
            "Classe ce document BTP (CCTP, CCAP, BPU, DPGF, plan, devis, "
            f"compte-rendu, autre) et extrais les métadonnées clés. {context.prompt}"
        )
        response = await client.complete([LLMMessage("user", prompt)])
        return AgentResult(
            agent=self.name,
            provider=response.provider,
            summary=response.text,
            output={"kind": "autre", "metadata": {}, "ocr_text": None},
        )
