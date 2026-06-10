"""Extraction tolérante de JSON depuis une réponse LLM.

Les modèles encadrent parfois le JSON de texte (```json ... ``` ou préambule).
`extract_json` isole le premier objet/array valide et le parse, en renvoyant
`None` si rien d'exploitable n'est trouvé (cas du provider mock hors-ligne).
"""

from __future__ import annotations

import json
from typing import Any


def extract_json(text: str) -> Any | None:
    text = text.strip()
    # Retire un éventuel bloc de code Markdown.
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Repli : isole la première accolade/crochet équilibré.
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    return None
