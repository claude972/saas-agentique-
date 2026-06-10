"""Persistance des devis (devis JSON → modèle relationnel)."""

from __future__ import annotations

from btp.database.models import Quote, QuoteLine
from sqlalchemy.orm import Session

from . import QuoteDraft


def persist_quote(session: Session, *, project_id: str, draft: QuoteDraft) -> Quote:
    """Crée un `Quote` et ses lignes à partir d'un brouillon, total calculé."""
    quote = Quote(
        project_id=project_id,
        reference=draft.reference,
        total_ht=draft.total_ht,
    )
    session.add(quote)
    session.flush()

    for position, line in enumerate(draft.lines, start=1):
        session.add(
            QuoteLine(
                quote_id=quote.id,
                position=position,
                designation=line.designation,
                unit=line.unit,
                quantity=line.quantity,
                unit_price=line.unit_price,
            )
        )
    session.flush()
    return quote
