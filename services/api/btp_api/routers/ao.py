"""Appels d'offres (Sprints 7-8-9).

Workflow (SRS) : Crawler → Détection → Téléchargement → Analyse → Qualification
→ GO / NO-GO → TenderAgent → Dossier final.

- Sprint 7 : enregistrement des AO détectés + qualification GO/NO-GO.
- Sprint 8 : ConsultationAgent (lecture CCTP/CCAP/BPU/DPGF des documents).
- Sprint 9 : TenderAgent (mémoire technique archivée comme document).
"""

from __future__ import annotations

from typing import Annotated

from btp.agents import AgentContext, get_agent
from btp.ao import qualify
from btp.auth.rbac import Action, Resource
from btp.database.models import Document, Project, Tender, User
from btp.database.models.enums import DocumentKind
from btp.documents import get_object_store
from btp_crawler import process
from btp_crawler.boamp import search as boamp_search
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import (
    ConsultationAnalyzeRequest,
    TenderCreate,
    TenderOut,
    TenderQualifyRequest,
    TenderResponseOut,
)


class TenderDetectRequest(BaseModel):
    keywords: str = Field(min_length=2)
    limit: int = Field(default=10, ge=1, le=50)

router = APIRouter(tags=["ao"])

_read = Annotated[User, Depends(require_permission(Resource.AO, Action.READ))]
_write = Annotated[User, Depends(require_permission(Resource.AO, Action.WRITE))]


def _tender_or_404(db: DbSession, tender_id: str) -> Tender:
    tender = db.get(Tender, tender_id)
    if tender is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AO introuvable")
    return tender


# --- Sprint 7 : détection / qualification -------------------------------------
@router.post(
    "/projects/{project_id}/tenders",
    response_model=TenderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_tender(
    project_id: str, payload: TenderCreate, db: DbSession, _: _write
) -> Tender:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    tender = Tender(
        project_id=project_id,
        title=payload.title,
        source_url=payload.source_url,
        buyer=payload.buyer,
    )
    db.add(tender)
    db.flush()
    return tender


@router.post(
    "/projects/{project_id}/tenders/detect",
    response_model=list[TenderOut],
    status_code=status.HTTP_201_CREATED,
)
def detect_tenders(
    project_id: str, payload: TenderDetectRequest, db: DbSession, _: _write
) -> list[Tender]:
    """Détecte des AO sur le BOAMP, les importe et les pré-qualifie (GO/NO-GO)."""
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")

    detected = boamp_search(payload.keywords, limit=payload.limit)
    created: list[Tender] = []
    for item in detected:
        qualification = process(item)
        tender = Tender(
            project_id=project_id,
            title=item.title,
            source_url=item.url or None,
            buyer=item.buyer,
            decision=qualification.decision,
            qualification=qualification.rationale,
        )
        db.add(tender)
        created.append(tender)
    db.flush()
    return created


@router.get("/projects/{project_id}/tenders", response_model=list[TenderOut])
def list_tenders(project_id: str, db: DbSession, _: _read) -> list[Tender]:
    stmt = (
        select(Tender)
        .where(Tender.project_id == project_id)
        .order_by(Tender.created_at.desc())
    )
    return list(db.scalars(stmt))


@router.post("/tenders/{tender_id}/qualify", response_model=TenderOut)
def qualify_tender(
    tender_id: str, payload: TenderQualifyRequest, db: DbSession, _: _write
) -> Tender:
    """Décision GO / NO-GO à partir d'un score de pertinence (0..1)."""
    tender = _tender_or_404(db, tender_id)
    result = qualify(score=payload.score, threshold=payload.threshold)
    tender.decision = result.decision
    tender.qualification = result.rationale
    db.flush()
    return tender


# --- Sprint 8 : ConsultationAgent ---------------------------------------------
@router.post("/projects/{project_id}/consultation/analyze")
async def analyze_consultation(
    project_id: str, payload: ConsultationAnalyzeRequest, db: DbSession, _: _write
) -> dict[str, object]:
    """Analyse les pièces de consultation (documents déjà OCR-isés)."""
    docs = list(
        db.scalars(
            select(Document).where(
                Document.id.in_(payload.document_ids),
                Document.project_id == project_id,
            )
        )
    )
    if not docs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documents introuvables")

    corpus = "\n\n".join(f"## {d.filename}\n{d.ocr_text or ''}" for d in docs)
    agent = get_agent("ConsultationAgent")
    result = await agent.run(AgentContext(project_id=project_id, prompt=corpus))
    return result.output


# --- Sprint 9 : TenderAgent ----------------------------------------------------
@router.post("/tenders/{tender_id}/respond", response_model=TenderResponseOut)
async def respond_tender(tender_id: str, db: DbSession, _: _write) -> TenderResponseOut:
    """Rédige la mémoire technique (TenderAgent) et l'archive comme document."""
    tender = _tender_or_404(db, tender_id)
    agent = get_agent("TenderAgent")
    result = await agent.run(
        AgentContext(
            project_id=tender.project_id,
            prompt=f"{tender.title}\n{tender.qualification or ''}",
        )
    )
    memo = str(result.output.get("memoire_technique") or result.summary)

    filename = f"memoire_technique_{tender.id[:8]}.md"
    key = f"projects/{tender.project_id}/tenders/{tender.id}/{filename}"
    get_object_store().put(key, memo.encode("utf-8"), content_type="text/markdown")
    document = Document(
        project_id=tender.project_id,
        filename=filename,
        s3_key=key,
        mime_type="text/markdown",
        kind=DocumentKind.AUTRE,
        ocr_text=memo,
    )
    db.add(document)
    db.flush()
    return TenderResponseOut(document_id=document.id, memoire_technique=memo)
