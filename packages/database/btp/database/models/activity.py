"""Journal d'activité (historique projet, activité des agents)."""

from __future__ import annotations

from btp.database.base import Base, TimestampMixin, UUIDMixin
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class ActivityLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "activity_logs"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"))
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    # acteur lisible : "user:alice" ou "agent:PhotoAgent"
    actor: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
