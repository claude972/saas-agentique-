"""Authentification et contrôle d'accès — BTP Agent Platform."""

from btp.auth.passwords import hash_password, verify_password
from btp.auth.rbac import (
    PERMISSIONS_BY_ROLE,
    Action,
    Permission,
    Resource,
    has_permission,
    permissions_for,
)
from btp.auth.tokens import TokenError, create_access_token, decode_access_token

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "TokenError",
    "Permission",
    "Resource",
    "Action",
    "PERMISSIONS_BY_ROLE",
    "has_permission",
    "permissions_for",
]
