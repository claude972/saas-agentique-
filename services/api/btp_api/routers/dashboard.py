"""Tableau de bord : agrégats et activité récente."""

from __future__ import annotations

from typing import Annotated

from btp.auth.rbac import Action, Resource
from btp.database.models import Project, Quote, Report, Tender, User
from btp.database.models.enums import ProjectStatus, TenderDecision
from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from btp_api.deps import DbSession, require_permission

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_read = Annotated[User, Depends(require_permission(Resource.PROJECTS, Action.READ))]


@router.get("/stats")
def dashboard_stats(db: DbSession, _: _read) -> dict[str, object]:
    projects_active = db.scalar(
        select(func.count())
        .select_from(Project)
        .where(Project.status != ProjectStatus.ARCHIVE)
    )
    quotes_count = db.scalar(select(func.count()).select_from(Quote)) or 0
    quotes_total = db.scalar(select(func.coalesce(func.sum(Quote.total_ht), 0))) or 0
    tenders_total = db.scalar(select(func.count()).select_from(Tender)) or 0
    tenders_go = db.scalar(
        select(func.count()).select_from(Tender).where(Tender.decision == TenderDecision.GO)
    )
    reports_count = db.scalar(select(func.count()).select_from(Report)) or 0

    recent_quotes = db.scalars(
        select(Quote).order_by(Quote.created_at.desc()).limit(5)
    ).all()
    recent_tenders = db.scalars(
        select(Tender).order_by(Tender.created_at.desc()).limit(5)
    ).all()

    return {
        "projects_active": projects_active or 0,
        "quotes_count": quotes_count,
        "quotes_total_ht": float(quotes_total),
        "tenders_total": tenders_total,
        "tenders_go": tenders_go or 0,
        "reports_count": reports_count,
        "agents_count": 6,
        "recent_quotes": [
            {
                "id": q.id,
                "reference": q.reference,
                "total_ht": float(q.total_ht),
                "status": q.status.value,
            }
            for q in recent_quotes
        ],
        "recent_tenders": [
            {
                "id": t.id,
                "title": t.title,
                "buyer": t.buyer,
                "decision": t.decision.value,
            }
            for t in recent_tenders
        ],
    }
