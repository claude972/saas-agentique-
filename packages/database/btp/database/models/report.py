"""Modèle compte-rendu."""

from __future__ import annotations

from typing import TYPE_CHECKING

from btp.database.base import Base, TimestampMixin, UUIDMixin
from btp.database.models.enums import ReportKind
from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from btp.database.models.project import Project


class Report(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reports"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    kind: Mapped[ReportKind] = mapped_column(
        Enum(ReportKind, native_enum=False, length=32),
        default=ReportKind.CHANTIER,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pdf_s3_key: Mapped[str | None] = mapped_column(String(1024))

    project: Mapped[Project] = relationship(back_populates="reports")
