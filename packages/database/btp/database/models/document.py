"""Modèles documents et photos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from btp.database.base import Base, TimestampMixin, UUIDMixin
from btp.database.models.enums import DocumentKind
from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from btp.database.models.project import Project


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    s3_key: Mapped[str | None] = mapped_column(String(1024))
    mime_type: Mapped[str | None] = mapped_column(String(120))
    kind: Mapped[DocumentKind] = mapped_column(
        Enum(DocumentKind, native_enum=False, length=32),
        default=DocumentKind.AUTRE,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project | None] = relationship(back_populates="documents")


class Photo(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "photos"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    s3_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    caption: Mapped[str | None] = mapped_column(String(512))
    # Sortie structurée du PhotoAgent (description, ouvrages, quantités, anomalies)
    analysis: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project | None] = relationship(back_populates="photos")
