"""Dépendances FastAPI : session DB, utilisateur courant, garde RBAC."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Annotated

from btp.auth import TokenError, decode_access_token, has_permission
from btp.auth.rbac import Action, Resource
from btp.database import get_session
from btp.database.models import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Iterator[Session]:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except TokenError as exc:
        raise credentials_exc from exc

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exc
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(resource: Resource, action: Action) -> Callable[[User], User]:
    """Dépendance vérifiant que l'utilisateur courant a la permission requise."""

    def _guard(user: CurrentUser) -> User:
        if not has_permission(user.role, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission requise: {resource.value}:{action.value}",
            )
        return user

    return _guard
