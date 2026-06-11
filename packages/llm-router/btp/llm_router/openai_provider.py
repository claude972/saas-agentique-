"""Connecteur générique compatible API OpenAI.

Un seul client couvre les fournisseurs exposant l'API « chat completions » de
type OpenAI : **GPT** (OpenAI), **Gemini** (endpoint compatible Google),
**Mistral** et **DeepSeek**. Le SDK `openai` est importé paresseusement pour
préserver le mode hors-ligne (provider mock).
"""

from __future__ import annotations

import base64

from btp.llm_router.providers import LLMMessage, LLMProvider, LLMResponse


def _data_uri(data: bytes) -> str:
    # Détection MIME minimale (PNG/JPEG/GIF/WEBP) pour le bloc image_url.
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    elif data[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif data[:6] in (b"GIF87a", b"GIF89a"):
        mime = "image/gif"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        mime = "image/webp"
    else:
        mime = "image/jpeg"
    return f"data:{mime};base64,{base64.standard_b64encode(data).decode('ascii')}"


class OpenAICompatibleProvider(LLMProvider):
    """Fournisseur LLM via API compatible OpenAI (base_url + clé configurables)."""

    def __init__(self, *, name: str, api_key: str, base_url: str, model: str) -> None:
        self.name = name
        self._api_key = api_key
        self._base_url = base_url
        self.model = model

    def _client(self):  # noqa: ANN202 - type fourni par le SDK importé paresseusement
        from openai import AsyncOpenAI  # import paresseux (offline-safe)

        return AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)

    async def _chat(self, messages: list[dict[str, object]]) -> LLMResponse:
        client = self._client()
        resp = await client.chat.completions.create(
            model=self.model, messages=messages, max_tokens=4000
        )
        choice = resp.choices[0].message.content or ""
        usage = {}
        if resp.usage is not None:
            usage = {
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
            }
        return LLMResponse(text=choice, provider=self.name, model=self.model, usage=usage)

    async def complete(
        self, messages: list[LLMMessage], *, model: str | None = None, **kwargs: object
    ) -> LLMResponse:
        if model:
            self.model = model
        payload = [{"role": m.role, "content": m.content} for m in messages]
        return await self._chat(payload)

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
        payload: list[dict[str, object]] = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "user"
        ]
        last_user = next((m for m in reversed(messages) if m.role == "user"), None)
        content: list[dict[str, object]] = [
            {"type": "text", "text": last_user.content if last_user else ""}
        ]
        content += [
            {"type": "image_url", "image_url": {"url": _data_uri(img)}} for img in images
        ]
        payload.append({"role": "user", "content": content})
        return await self._chat(payload)
