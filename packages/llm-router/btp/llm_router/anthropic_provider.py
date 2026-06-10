"""Intégration réelle du fournisseur Anthropic (Claude).

Implémente l'interface `LLMProvider` via le SDK officiel `anthropic` (client
asynchrone). Le SDK est importé paresseusement pour que le mode hors-ligne
(provider mock) n'ait aucune dépendance réseau.

Conventions (cf. recommandations SDK Claude) :
- modèle par défaut `claude-opus-4-8` ;
- pensée adaptative (`thinking={"type": "adaptive"}`) pour les tâches complexes ;
- streaming + `get_final_message()` pour éviter les timeouts sur longues sorties.
"""

from __future__ import annotations

import base64
import os

from btp.llm_router.providers import LLMMessage, LLMProvider, LLMResponse

_DEFAULT_MODEL = "claude-opus-4-8"
_DEFAULT_MAX_TOKENS = 8000


def _media_type(data: bytes) -> str:
    """Devine le type MIME d'une image à partir de ses premiers octets."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _split_system(messages: list[LLMMessage]) -> tuple[str | None, list[dict[str, object]]]:
    system_parts = [m.content for m in messages if m.role == "system"]
    convo = [
        {"role": m.role, "content": m.content}
        for m in messages
        if m.role in ("user", "assistant")
    ]
    system = "\n\n".join(system_parts) if system_parts else None
    return system, convo


class AnthropicProvider(LLMProvider):
    """Fournisseur Claude réel (utilisé dès qu'une clé API est configurée)."""

    name = "claude"

    def __init__(self, *, model: str | None = None, max_tokens: int | None = None) -> None:
        self.model = model or os.getenv("ANTHROPIC_MODEL", _DEFAULT_MODEL)
        self.max_tokens = max_tokens or int(
            os.getenv("ANTHROPIC_MAX_TOKENS", str(_DEFAULT_MAX_TOKENS))
        )

    def _client(self):  # noqa: ANN202 - type fourni par le SDK importé paresseusement
        from anthropic import AsyncAnthropic  # import paresseux (offline-safe)

        return AsyncAnthropic()

    async def _run(
        self, system: str | None, messages: list[dict[str, object]]
    ) -> LLMResponse:
        client = self._client()
        # Streaming + get_final_message : robuste sur les sorties longues.
        async with client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system or "",
            thinking={"type": "adaptive"},
            messages=messages,
        ) as stream:
            final = await stream.get_final_message()

        text = "".join(b.text for b in final.content if b.type == "text")
        usage = {
            "input_tokens": getattr(final.usage, "input_tokens", 0),
            "output_tokens": getattr(final.usage, "output_tokens", 0),
        }
        return LLMResponse(text=text, provider=self.name, model=self.model, usage=usage)

    async def complete(
        self, messages: list[LLMMessage], *, model: str | None = None, **kwargs: object
    ) -> LLMResponse:
        if model:
            self.model = model
        system, convo = _split_system(messages)
        if not convo:
            convo = [{"role": "user", "content": ""}]
        return await self._run(system, convo)

    async def vision(
        self,
        messages: list[LLMMessage],
        images: list[bytes],
        *,
        model: str | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        if model:
            self.model = model
        system, convo = _split_system(messages)

        image_blocks = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": _media_type(img),
                    "data": base64.standard_b64encode(img).decode("ascii"),
                },
            }
            for img in images
        ]
        # Dernier message utilisateur enrichi des images.
        last_text = convo[-1]["content"] if convo else ""
        content: list[dict[str, object]] = [*image_blocks, {"type": "text", "text": last_text}]
        convo = convo[:-1] if convo else []
        convo.append({"role": "user", "content": content})
        return await self._run(system, convo)
