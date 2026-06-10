"""Gestion des utilisateurs (réservée à l'Admin — permission users:manage)."""

from __future__ import annotations

from typing import Annotated

from btp.auth import hash_password
from btp.auth.rbac import Action, Resource
from btp.database.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

_admin_read = Annotated[User, Depends(require_permission(Resource.USERS, Action.READ))]
_admin_write = Annotated[User, Depends(require_permission(Resource.USERS, Action.WRITE))]


@router.get("", response_model=list[UserOut])
def list_users(db: DbSession, _: _admin_read) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at)))


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: DbSession, _: _admin_write) -> User:
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà",
        ) from exc
    return user
