"""Modèles devis."""

from __future__ import annotations

from typing import TYPE_CHECKING

from btp.database.base import Base, TimestampMixin, UUIDMixin
from btp.database.models.enums import QuoteStatus
from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from btp.database.models.project import Project


class Quote(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "quotes"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False)
    reference: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[QuoteStatus] = mapped_column(
        Enum(QuoteStatus, native_enum=False, length=32),
        default=QuoteStatus.BROUILLON,
        nullable=False,
    )
    total_ht: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    pdf_s3_key: Mapped[str | None] = mapped_column(String(1024))

    project: Mapped[Project] = relationship(back_populates="quotes")
    lines: Mapped[list[QuoteLine]] = relationship(
        back_populates="quote", cascade="all, delete-orphan"
    )


class QuoteLine(UUIDMixin, Base):
    __tablename__ = "quote_lines"

    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)
    designation: Mapped[str] = mapped_column(String(512), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="u")
    quantity: Mapped[float] = mapped_column(Numeric(12, 3), default=0)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    quote: Mapped[Quote] = relationship(back_populates="lines")

    @property
    def total(self) -> float:
        return float(self.quantity) * float(self.unit_price)
