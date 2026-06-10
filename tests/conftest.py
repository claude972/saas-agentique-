"""Fixtures partagées : base SQLite isolée + client API authentifié."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

import pytest


@pytest.fixture(scope="session", autouse=True)
def _env() -> Iterator[None]:
    """Force une base SQLite temporaire et une clé de test avant tout import."""
    tmpdir = tempfile.mkdtemp()
    os.environ["DATABASE_URL"] = f"sqlite:///{tmpdir}/test.db"
    os.environ["SECRET_KEY"] = "test-secret-key-please-do-not-use-in-prod-0123456789"
    yield


@pytest.fixture()
def db_session():
    from btp.database import init_db, session_scope

    init_db()
    with session_scope() as session:
        yield session


@pytest.fixture()
def admin_token() -> str:
    from btp.auth import create_access_token, hash_password
    from btp.database import init_db, session_scope
    from btp.database.models import User
    from btp.database.models.enums import UserRole

    init_db()
    with session_scope() as session:
        user = session.query(User).filter_by(email="admin@test.local").one_or_none()
        if user is None:
            user = User(
                email="admin@test.local",
                hashed_password=hash_password("password123"),
                full_name="Admin Test",
                role=UserRole.ADMIN,
            )
            session.add(user)
            session.flush()
        return create_access_token(user.id, role=user.role.value)


@pytest.fixture()
def client():
    from btp_api.main import app
    from fastapi.testclient import TestClient

    return TestClient(app)
