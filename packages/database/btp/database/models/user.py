"""Modèle utilisateur."""

from __future__ import annotations

from btp.database.base import Base, TimestampMixin, UUIDMixin
from btp.database.models.enums import UserRole
from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=32),
        default=UserRole.LECTURE_SEULE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.email} ({self.role.value})>"
