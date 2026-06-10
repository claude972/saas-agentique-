"""Hachage et vérification des mots de passe."""

from __future__ import annotations

from passlib.context import CryptContext

# pbkdf2_sha256 : pur Python, sans dépendance native, robuste en CI.
# bcrypt/argon2 restent activables en production via la même interface.
_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(plain, hashed)
    except ValueError:
        return False
