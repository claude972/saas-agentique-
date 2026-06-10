"""Tests de l'orchestration agentique (hors-ligne, provider mock)."""

from __future__ import annotations

import pytest
from btp.agents import AgentContext, SupervisorAgent
from btp.ao import qualify
from btp.database.models.enums import TenderDecision


def test_supervisor_plans_photo_and_quote():
    supervisor = SupervisorAgent()
    plan = supervisor.plan(AgentContext(prompt="Analyse cette photo et fais un devis"))
    assert "PhotoAgent" in plan.agents
    assert "QuoteAgent" in plan.agents
    # PhotoAgent → QuoteAgent doit s'exécuter en séquence (dépendance de données).
    assert plan.parallel is False


def test_supervisor_defaults_to_document_agent():
    supervisor = SupervisorAgent()
    plan = supervisor.plan(AgentContext(prompt="bonjour"))
    assert plan.agents == ["DocumentAgent"]


@pytest.mark.asyncio
async def test_supervisor_runs_offline():
    supervisor = SupervisorAgent()
    result = await supervisor.run(AgentContext(prompt="Rédige un compte-rendu de réunion"))
    assert result["plan"]["agents"] == ["ReportAgent"]
    assert "ReportAgent" in result["summary"]


def test_ao_qualification_go_no_go():
    assert qualify(score=0.8).decision is TenderDecision.GO
    assert qualify(score=0.2).decision is TenderDecision.NO_GO
