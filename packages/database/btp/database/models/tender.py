"""Modèle appel d'offres (AO)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from btp.database.base import Base, TimestampMixin, UUIDMixin
from btp.database.models.enums import TenderDecision
from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from btp.database.models.project import Project


class Tender(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "tenders"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024))
    buyer: Mapped[str | None] = mapped_column(String(255))
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision: Mapped[TenderDecision] = mapped_column(
        Enum(TenderDecision, native_enum=False, length=32),
        default=TenderDecision.A_QUALIFIER,
        nullable=False,
    )
    # Résultat de la qualification (synthèse, score) produit par l'analyse
    qualification: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project | None] = relationship(back_populates="tenders")
