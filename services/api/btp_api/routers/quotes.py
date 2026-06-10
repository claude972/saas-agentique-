"""Devis (Sprint 5) : génération assistée, persistance, PDF, archivage.

Workflow (SRS) : description → QuoteAgent → Devis JSON → PDF → Archivage.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from btp.agents import AgentContext, get_agent
from btp.auth.rbac import Action, Resource
from btp.database.models import Project, Quote, User
from btp.documents import get_object_store
from btp.quotes import QuoteDraft, QuoteLineDraft, persist_quote, render_quote_pdf
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import QuoteDetail, QuoteGenerateRequest, QuoteOut

router = APIRouter(tags=["quotes"])

_read = Annotated[User, Depends(require_permission(Resource.QUOTES, Action.READ))]
_write = Annotated[User, Depends(require_permission(Resource.QUOTES, Action.WRITE))]


def _quote_or_404(db: DbSession, quote_id: str) -> Quote:
    quote = db.get(Quote, quote_id)
    if quote is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis introuvable")
    return quote


def _draft_from_quote(quote: Quote) -> QuoteDraft:
    return QuoteDraft(
        reference=quote.reference,
        lines=[
            QuoteLineDraft(
                designation=line.designation,
                unit=line.unit,
                quantity=float(line.quantity),
                unit_price=float(line.unit_price),
            )
            for line in sorted(quote.lines, key=lambda line: line.position)
        ],
    )


@router.post(
    "/projects/{project_id}/quotes/generate",
    response_model=QuoteDetail,
    status_code=status.HTTP_201_CREATED,
)
async def generate_quote(
    project_id: str, payload: QuoteGenerateRequest, db: DbSession, _: _write
) -> Quote:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")

    agent = get_agent("QuoteAgent")
    result = await agent.run(AgentContext(project_id=project_id, prompt=payload.description))
    devis = result.output.get("devis", {})
    lines = [
        QuoteLineDraft(
            designation=line["designation"],
            unit=line["unite"],
            quantity=line["quantite"],
            unit_price=line["prix_unitaire"],
        )
        for line in devis.get("lignes", [])
    ]
    reference = f"DEV-{uuid.uuid4().hex[:8].upper()}"
    draft = QuoteDraft(reference=reference, lines=lines)
    return persist_quote(db, project_id=project_id, draft=draft)


@router.get("/projects/{project_id}/quotes", response_model=list[QuoteOut])
def list_quotes(project_id: str, db: DbSession, _: _read) -> list[Quote]:
    stmt = (
        select(Quote)
        .where(Quote.project_id == project_id)
        .order_by(Quote.created_at.desc())
    )
    return list(db.scalars(stmt))


@router.get("/quotes/{quote_id}", response_model=QuoteDetail)
def get_quote(quote_id: str, db: DbSession, _: _read) -> Quote:
    return _quote_or_404(db, quote_id)


@router.post("/quotes/{quote_id}/pdf", response_model=QuoteOut)
def build_quote_pdf(quote_id: str, db: DbSession, _: _write) -> Quote:
    """Génère le PDF du devis, l'archive (object store) et mémorise sa clé."""
    quote = _quote_or_404(db, quote_id)
    project = db.get(Project, quote.project_id)
    pdf = render_quote_pdf(
        _draft_from_quote(quote),
        project_name=project.name if project else "",
        client_name=project.client.name if project and project.client else "",
    )
    key = f"quotes/{quote.id}/{quote.reference}.pdf"
    get_object_store().put(key, pdf, content_type="application/pdf")
    quote.pdf_s3_key = key
    db.flush()
    return quote


@router.get("/quotes/{quote_id}/pdf")
def download_quote_pdf(quote_id: str, db: DbSession, _: _read) -> Response:
    quote = _quote_or_404(db, quote_id)
    store = get_object_store()
    if quote.pdf_s3_key and store.exists(quote.pdf_s3_key):
        pdf = store.get(quote.pdf_s3_key)
    else:
        project = db.get(Project, quote.project_id)
        pdf = render_quote_pdf(
            _draft_from_quote(quote),
            project_name=project.name if project else "",
        )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{quote.reference}.pdf"'},
    )
