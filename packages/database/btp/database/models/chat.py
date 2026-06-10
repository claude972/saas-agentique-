"""Modèles de conversation (chat par projet, mémoire persistante)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from btp.database.base import Base, TimestampMixin, UUIDMixin
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    pass


class Conversation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str | None] = mapped_column(String(255))

    messages: Mapped[list[ChatMessage]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "chat_messages"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id"), nullable=False
    )
    # role : user | assistant | system | agent:<name>
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Trace optionnelle de l'agent/LLM ayant produit le message (JSON sérialisé)
    meta: Mapped[str | None] = mapped_column(Text)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
