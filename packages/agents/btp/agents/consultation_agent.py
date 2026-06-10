"""ConsultationAgent — lecture des pièces de consultation (CCTP, CCAP, BPU, DPGF, plans)."""

from __future__ import annotations

from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.llm_router import LLMMessage, TaskType


class ConsultationAgent(BaseAgent):
    name = "ConsultationAgent"
    description = "Lecture et synthèse des pièces de consultation (CCTP, CCAP, BPU, DPGF, plans)."

    async def run(self, context: AgentContext) -> AgentResult:
        # Gros PDF → Gemini (cf. SRS).
        client = self.router.client_for(TaskType.LARGE_PDF)
        prompt = (
            "Analyse les pièces de consultation BTP fournies (CCTP, CCAP, BPU, "
            "DPGF, plans). Extrais les exigences techniques, contraintes, "
            f"quantités et points de vigilance. {context.prompt}"
        )
        response = await client.complete([LLMMessage("user", prompt)])
        return AgentResult(
            agent=self.name,
            provider=response.provider,
            summary=response.text,
            output={"exigences": [], "contraintes": [], "synthese": response.text},
        )
