"""SupervisorAgent — orchestration des agents spécialisés.

Mission (SRS) :
1. comprendre la demande utilisateur ;
2. choisir les agents pertinents ;
3. construire le workflow ;
4. fusionner les résultats.

La sélection est ici fondée sur des heuristiques de mots-clés (déterministe,
testable hors-ligne). L'intégration LLM (planification via Claude) viendra
remplacer `plan()` au Sprint 3 sans changer l'interface publique.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from btp.agents.base import AgentContext, AgentResult, BaseAgent
from btp.agents.registry import get_agent
from btp.llm_router import LLMRouter


@dataclass
class Plan:
    agents: list[str]
    parallel: bool = False
    rationale: str = ""


# Mots-clés → agent (heuristique de planification par défaut).
_KEYWORD_ROUTING: list[tuple[tuple[str, ...], str]] = [
    (("photo", "image", "chantier visuel", "anomalie"), "PhotoAgent"),
    (("devis", "chiffrage", "quantif", "prix"), "QuoteAgent"),
    (("cctp", "ccap", "bpu", "dpgf", "consultation", "plan"), "ConsultationAgent"),
    (("appel d'offre", "ao", "mémoire technique", "memoire", "soumission"), "TenderAgent"),
    (("compte-rendu", "compte rendu", "cr ", "réunion", "visite", "réserve"), "ReportAgent"),
    (("document", "classer", "ocr", "extraction", "recherche"), "DocumentAgent"),
]


class SupervisorAgent:
    def __init__(self, router: LLMRouter | None = None) -> None:
        self.router = router

    def plan(self, context: AgentContext) -> Plan:
        """Sélectionne les agents en fonction de la demande."""
        text = f"{context.prompt} {' '.join(context.inputs.keys())}".lower()
        selected: list[str] = []
        for keywords, agent in _KEYWORD_ROUTING:
            if any(k in text for k in keywords) and agent not in selected:
                selected.append(agent)

        # Workflow devis : une photo implique aussi un chiffrage en aval.
        if "PhotoAgent" in selected and "QuoteAgent" not in selected and "devis" in text:
            selected.append("QuoteAgent")

        if not selected:
            selected = ["DocumentAgent"]

        # Sécuriser : PhotoAgent doit précéder QuoteAgent (dépendance de données).
        parallel = not ("PhotoAgent" in selected and "QuoteAgent" in selected)
        return Plan(agents=selected, parallel=parallel, rationale=f"matched on: {text[:80]}")

    def _instantiate(self, name: str) -> BaseAgent:
        agent = get_agent(name)
        if self.router is not None:
            agent.router = self.router
        return agent

    async def run(self, context: AgentContext) -> dict[str, object]:
        plan = self.plan(context)
        agents = [self._instantiate(name) for name in plan.agents]

        results: list[AgentResult]
        if plan.parallel:
            results = list(await asyncio.gather(*(a.run(context) for a in agents)))
        else:
            results = []
            ctx = context
            for agent in agents:
                res = await agent.run(ctx)
                results.append(res)
                # Chaînage : la sortie alimente l'entrée de l'agent suivant.
                ctx = AgentContext(
                    project_id=ctx.project_id,
                    prompt=ctx.prompt,
                    inputs={**ctx.inputs, **res.output},
                    history=ctx.history,
                )

        return self.merge(plan, results)

    def merge(self, plan: Plan, results: list[AgentResult]) -> dict[str, object]:
        """Fusionne les résultats des agents en une réponse unique."""
        return {
            "plan": {"agents": plan.agents, "parallel": plan.parallel},
            "results": [
                {
                    "agent": r.agent,
                    "summary": r.summary,
                    "provider": r.provider,
                    "output": r.output,
                }
                for r in results
            ],
            "summary": "\n\n".join(f"## {r.agent}\n{r.summary}" for r in results),
        }
