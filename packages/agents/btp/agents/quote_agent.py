"""QuoteAgent — analyse, quantification, chiffrage et génération de devis.

Demande au LLM un devis structuré (JSON) et le normalise en lignes exploitables
par `btp.quotes`. Hors-ligne (provider mock), retourne un devis vide proprement.
"""

from __future__ import annotations

from typing import Any

from btp.agents._json import extract_json
from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.llm_router import LLMMessage, TaskType

_SYSTEM = (
    "Tu es un économiste de la construction (BTP). À partir de la description "
    "d'ouvrages et de quantités, tu produis un devis structuré. Réponds "
    "UNIQUEMENT par un objet JSON de la forme : "
    '{"lignes": [{"designation": str, "unite": str, "quantite": number, '
    '"prix_unitaire": number}]}. Les prix sont en euros HT.'
)


def _normalize_lines(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    raw = payload.get("lignes", [])
    lines: list[dict[str, Any]] = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        try:
            lines.append(
                {
                    "designation": str(item.get("designation", "")).strip(),
                    "unite": str(item.get("unite", "u")).strip() or "u",
                    "quantite": float(item.get("quantite", 0) or 0),
                    "prix_unitaire": float(item.get("prix_unitaire", 0) or 0),
                }
            )
        except (TypeError, ValueError):
            continue
    return [line for line in lines if line["designation"]]


class QuoteAgent(BaseAgent):
    name = "QuoteAgent"
    description = "Quantification et chiffrage : génère et révise des devis."

    async def run(self, context: AgentContext) -> AgentResult:
        client = self.router.client_for(TaskType.COMPLEX_WRITING)
        source = context.inputs.get("description", context.prompt)
        prompt = (
            "À partir des éléments suivants, produis le devis JSON demandé.\n\n"
            f"{source}"
        )
        response = await client.complete(
            [LLMMessage("system", _SYSTEM), LLMMessage("user", prompt)]
        )
        lines = _normalize_lines(extract_json(response.text))
        total = round(sum(line["quantite"] * line["prix_unitaire"] for line in lines), 2)
        return AgentResult(
            agent=self.name,
            provider=response.provider,
            summary=(
                f"Devis : {len(lines)} ligne(s), total {total:.2f} € HT."
                if lines
                else "Devis non structuré (aucune ligne extraite)."
            ),
            output={"devis": {"lignes": lines, "total_ht": total}, "raw": response.text},
        )
