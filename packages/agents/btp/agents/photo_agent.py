"""PhotoAgent — analyse de photos de chantier.

Entrées : jpg / png / pdf → description, ouvrages, quantités estimées, anomalies.
Routage : tâches de vision → GPT (cf. SRS), avec repli Claude si seule sa clé
est configurée. Demande une sortie JSON structurée.
"""

from __future__ import annotations

from typing import Any

from btp.agents._json import extract_json
from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.llm_router import LLMMessage, TaskType

_SYSTEM = (
    "Tu es conducteur de travaux BTP. Analyse la photo de chantier et réponds "
    "UNIQUEMENT par un objet JSON : {\"description\": str, \"ouvrages\": [str], "
    "\"quantites_estimees\": [{\"ouvrage\": str, \"quantite\": number, \"unite\": str}], "
    "\"anomalies\": [str]}."
)


def _coerce(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"description": "", "ouvrages": [], "quantites_estimees": [], "anomalies": []}
    return {
        "description": str(payload.get("description", "")),
        "ouvrages": list(payload.get("ouvrages", []) or []),
        "quantites_estimees": list(payload.get("quantites_estimees", []) or []),
        "anomalies": list(payload.get("anomalies", []) or []),
    }


class PhotoAgent(BaseAgent):
    name = "PhotoAgent"
    description = "Analyse des photos de chantier (ouvrages, quantités, anomalies)."

    async def run(self, context: AgentContext) -> AgentResult:
        client = self.router.client_for(TaskType.PHOTO_ANALYSIS)
        images: list[bytes] = context.inputs.get("images", [])
        prompt = f"Contexte: {context.prompt}" if context.prompt else "Analyse cette photo."
        response = await client.vision(
            [LLMMessage("system", _SYSTEM), LLMMessage("user", prompt)],
            images=images,
        )
        data = _coerce(extract_json(response.text))
        if not data["description"]:
            data["description"] = response.text
        return AgentResult(
            agent=self.name,
            provider=response.provider,
            summary=data["description"],
            output=data,
        )
