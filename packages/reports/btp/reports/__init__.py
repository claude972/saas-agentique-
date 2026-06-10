"""Services métier comptes-rendus.

Workflow (SRS) : Photo / Audio / Texte → ReportAgent → Compte-rendu →
Validation → Archivage.
"""

from __future__ import annotations

from btp.database.models import Report
from btp.database.models.enums import ReportKind
from sqlalchemy.orm import Session

__all__ = ["create_report", "validate_report"]


def create_report(
    session: Session, *, project_id: str, title: str, kind: ReportKind = ReportKind.CHANTIER,
    content: str | None = None,
) -> Report:
    report = Report(project_id=project_id, title=title, kind=kind, content=content)
    session.add(report)
    session.flush()
    return report


def validate_report(session: Session, report: Report) -> Report:
    report.validated = True
    session.flush()
    return report
