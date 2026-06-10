"""Modèle projet."""

from __future__ import annotations

from typing import TYPE_CHECKING

from btp.database.base import Base, TimestampMixin, UUIDMixin
from btp.database.models.enums import ProjectStatus
from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from btp.database.models.crm import Client
    from btp.database.models.document import Document, Photo
    from btp.database.models.quote import Quote
    from btp.database.models.report import Report
    from btp.database.models.tender import Tender


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, native_enum=False, length=32),
        default=ProjectStatus.PROSPECT,
        nullable=False,
    )
    client_id: Mapped[str | None] = mapped_column(ForeignKey("clients.id"))

    client: Mapped[Client | None] = relationship(back_populates="projects")
    documents: Mapped[list[Document]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    photos: Mapped[list[Photo]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    quotes: Mapped[list[Quote]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    tenders: Mapped[list[Tender]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
