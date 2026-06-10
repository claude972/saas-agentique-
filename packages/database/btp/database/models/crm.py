"""Modèles CRM : clients, contacts, opportunités, interactions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from btp.database.base import Base, TimestampMixin, UUIDMixin
from btp.database.models.enums import OpportunityStage
from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from btp.database.models.project import Project


class Client(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "clients"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    siret: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)

    projects: Mapped[list[Project]] = relationship(back_populates="client")
    contacts: Mapped[list[Contact]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )
    opportunities: Mapped[list[Opportunity]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )


class Contact(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "contacts"

    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(40))

    client: Mapped[Client] = relationship(back_populates="contacts")


class Opportunity(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "opportunities"

    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[OpportunityStage] = mapped_column(
        Enum(OpportunityStage, native_enum=False, length=32),
        default=OpportunityStage.NOUVELLE,
        nullable=False,
    )
    amount: Mapped[float | None] = mapped_column(Numeric(14, 2))

    client: Mapped[Client] = relationship(back_populates="opportunities")


class Interaction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "interactions"

    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(40), default="note")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
