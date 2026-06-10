"""Comptes-rendus (Sprint 6) : génération ReportAgent + validation + archivage.

Workflow (SRS) : Photo / Audio / Texte → ReportAgent → Compte-rendu →
Validation → Archivage.
"""

from __future__ import annotations

from typing import Annotated

from btp.agents import AgentContext, get_agent
from btp.auth.rbac import Action, Resource
from btp.database.models import Project, Report, User
from btp.reports import validate_report
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import ReportCreate, ReportOut

router = APIRouter(tags=["reports"])

_read = Annotated[User, Depends(require_permission(Resource.REPORTS, Action.READ))]
_write = Annotated[User, Depends(require_permission(Resource.REPORTS, Action.WRITE))]


def _report_or_404(db: DbSession, report_id: str) -> Report:
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Compte-rendu introuvable"
        )
    return report


@router.post(
    "/projects/{project_id}/reports/generate",
    response_model=ReportOut,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report(
    project_id: str, payload: ReportCreate, db: DbSession, _: _write
) -> Report:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")

    agent = get_agent("ReportAgent")
    result = await agent.run(
        AgentContext(
            project_id=project_id,
            prompt=payload.notes or payload.title,
            inputs={"kind": payload.kind.value},
        )
    )
    report = Report(
        project_id=project_id,
        kind=payload.kind,
        title=payload.title,
        content=str(result.output.get("content") or result.summary),
    )
    db.add(report)
    db.flush()
    return report


@router.get("/projects/{project_id}/reports", response_model=list[ReportOut])
def list_reports(project_id: str, db: DbSession, _: _read) -> list[Report]:
    stmt = (
        select(Report)
        .where(Report.project_id == project_id)
        .order_by(Report.created_at.desc())
    )
    return list(db.scalars(stmt))


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: str, db: DbSession, _: _read) -> Report:
    return _report_or_404(db, report_id)


@router.post("/reports/{report_id}/validate", response_model=ReportOut)
def validate(report_id: str, db: DbSession, _: _write) -> Report:
    report = _report_or_404(db, report_id)
    return validate_report(db, report)
