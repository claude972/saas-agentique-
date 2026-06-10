"""Exposition de l'architecture agentique (liste + invocation du Supervisor)."""

from __future__ import annotations

from typing import Annotated

from btp.agents import AgentContext, SupervisorAgent, list_agents
from btp.auth.rbac import Action, Resource
from btp.database.models import User
from fastapi import APIRouter, Depends

from btp_api.deps import require_permission
from btp_api.schemas import AgentInfo, SupervisorRequest

router = APIRouter(prefix="/agents", tags=["agents"])

_agents_read = Annotated[User, Depends(require_permission(Resource.AGENTS, Action.READ))]


@router.get("", response_model=list[AgentInfo])
def get_agents(_: _agents_read) -> list[dict[str, str]]:
    return list_agents()


@router.post("/supervisor")
async def run_supervisor(payload: SupervisorRequest, _: _agents_read) -> dict[str, object]:
    """Planifie et exécute un workflow d'agents pour la demande donnée.

    Hors-ligne (sans clés LLM), les agents répondent via le provider mock —
    le plan et l'orchestration restent pleinement fonctionnels.
    """
    supervisor = SupervisorAgent()
    context = AgentContext(
        project_id=payload.project_id,
        prompt=payload.prompt,
        inputs=payload.inputs,
    )
    return await supervisor.run(context)
