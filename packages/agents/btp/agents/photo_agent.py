"""PhotoAgent — analyse de photos de chantier.

Entrées : jpg / png / pdf → description, ouvrages, quantités estimées, anomalies.
Routage : tâches de vision → GPT (cf. SRS).
"""

from __future__ import annotations

from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.llm_router import LLMMessage, TaskType


class PhotoAgent(BaseAgent):
    name = "PhotoAgent"
    description = "Analyse des photos de chantier (ouvrages, quantités, anomalies)."

    async def run(self, context: AgentContext) -> AgentResult:
        client = self.router.client_for(TaskType.PHOTO_ANALYSIS)
        images: list[bytes] = context.inputs.get("images", [])
        prompt = (
            "Analyse cette photo de chantier BTP. Donne une description, la liste "
            "des ouvrages identifiés, une estimation des quantités et les anomalies "
            f"éventuelles. Contexte: {context.prompt}"
        )
        response = await client.vision([LLMMessage("user", prompt)], images=images)
        # Schéma de sortie attendu (à structurer par l'intégration réelle).
        return AgentResult(
            agent=self.name,
            provider=response.provider,
            summary=response.text,
            output={
                "description": response.text,
                "ouvrages": [],
                "quantites_estimees": [],
                "anomalies": [],
            },
        )
