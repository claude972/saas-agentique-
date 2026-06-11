"""Tests du routage multi-LLM et de la sélection des fournisseurs (hors réseau).

On vérifie la logique de sélection/repli sans appeler les API : construire le
client n'émet aucune requête, on inspecte seulement le type et le nom.
"""

from __future__ import annotations

import pytest
from btp.llm_router import EchoProvider, LLMRouter, Provider, TaskType, transcription_available
from btp.llm_router.openai_provider import OpenAICompatibleProvider

_KEYS = [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "MISTRAL_API_KEY",
    "DEEPSEEK_API_KEY",
]


@pytest.fixture()
def clean_env(monkeypatch):
    for key in _KEYS:
        monkeypatch.delenv(key, raising=False)
    return monkeypatch


def test_offline_uses_echo(clean_env):
    router = LLMRouter()
    assert isinstance(router.client_for(TaskType.PHOTO_ANALYSIS), EchoProvider)


def test_deepseek_only_handles_all_tasks(clean_env):
    clean_env.setenv("DEEPSEEK_API_KEY", "sk-test")
    router = LLMRouter()
    # Tâche routée vers GPT, mais seul DeepSeek est configuré → repli DeepSeek.
    client = router.client_for(TaskType.VISION)
    assert isinstance(client, OpenAICompatibleProvider)
    assert client.name == "deepseek"
    assert "deepseek" in client._base_url


def test_routed_provider_preferred_when_configured(clean_env):
    clean_env.setenv("MISTRAL_API_KEY", "sk-m")
    clean_env.setenv("OPENAI_API_KEY", "sk-o")
    router = LLMRouter()
    # CLASSIFICATION est routé vers Mistral (configuré) → Mistral, pas le repli.
    client = router.client_for(TaskType.CLASSIFICATION)
    assert client.name == "mistral"


def test_is_configured(clean_env):
    router = LLMRouter()
    assert router.is_configured(Provider.GPT) is False
    clean_env.setenv("OPENAI_API_KEY", "x")
    assert router.is_configured(Provider.GPT) is True


def test_transcription_unavailable_offline(clean_env):
    assert transcription_available() is False
