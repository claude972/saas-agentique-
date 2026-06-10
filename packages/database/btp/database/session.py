"""Gestion du moteur SQLAlchemy et des sessions."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from btp.database.base import Base
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./btp.db"


def _database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Retourne le moteur partagé (singleton)."""
    url = _database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, echo=False, future=True, connect_args=connect_args)


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_session() -> Session:
    """Crée une nouvelle session ORM (à fermer par l'appelant)."""
    return _session_factory()()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Contexte transactionnel : commit en sortie, rollback sur exception."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Crée toutes les tables. Importe les modèles pour peupler les métadonnées."""
    import btp.database.models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
