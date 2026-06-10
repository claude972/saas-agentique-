"""Couche d'accès aux données — BTP Agent Platform.

Expose la `Base` déclarative, les modèles ORM et les helpers de session.
"""

from btp.database.base import Base
from btp.database.session import (
    get_engine,
    get_session,
    init_db,
    session_scope,
)

__all__ = [
    "Base",
    "get_engine",
    "get_session",
    "session_scope",
    "init_db",
]
