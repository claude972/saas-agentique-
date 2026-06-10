"""Contrôle d'accès basé sur les rôles (RBAC).

Chaque rôle est associé à un ensemble de permissions atomiques
`Permission(resource, action)`. La matrice ci-dessous fait foi ; le tableau
de `docs/ARCHITECTURE.md` n'en est qu'un résumé.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from btp.database.models.enums import UserRole


class Resource(str, enum.Enum):
    USERS = "users"
    ROLES = "roles"
    SETTINGS = "settings"
    AGENTS = "agents"
    PROJECTS = "projects"
    DOCUMENTS = "documents"
    CRM = "crm"
    AO = "ao"
    QUOTES = "quotes"
    REPORTS = "reports"
    CHANTIER = "chantier"


class Action(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    MANAGE = "manage"  # implique read + write + administration


@dataclass(frozen=True)
class Permission:
    resource: Resource
    action: Action

    def __str__(self) -> str:
        return f"{self.resource.value}:{self.action.value}"


def _p(resource: Resource, action: Action) -> Permission:
    return Permission(resource, action)


def _crud(resource: Resource) -> set[Permission]:
    return {_p(resource, Action.READ), _p(resource, Action.WRITE)}


def _read(resource: Resource) -> set[Permission]:
    return {_p(resource, Action.READ)}


# --- Matrice rôle → permissions ------------------------------------------------

_ALL_RESOURCES = list(Resource)

_ADMIN: set[Permission] = {_p(r, Action.MANAGE) for r in _ALL_RESOURCES} | {
    _p(r, a) for r in _ALL_RESOURCES for a in (Action.READ, Action.WRITE)
}

_DIRECTION: set[Permission] = (
    _crud(Resource.PROJECTS)
    | _crud(Resource.AO)
    | _crud(Resource.CRM)
    | _crud(Resource.REPORTS)
    | _crud(Resource.QUOTES)
    | _crud(Resource.DOCUMENTS)
    | _crud(Resource.CHANTIER)
)

_CHARGE_AFFAIRES: set[Permission] = (
    _crud(Resource.QUOTES)
    | _crud(Resource.AO)
    | _crud(Resource.CRM)
    | _crud(Resource.DOCUMENTS)
    | _read(Resource.PROJECTS)
)

_CONDUCTEUR: set[Permission] = (
    _crud(Resource.CHANTIER)
    | _crud(Resource.REPORTS)
    | _crud(Resource.DOCUMENTS)
    | _read(Resource.PROJECTS)
)

_LECTURE_SEULE: set[Permission] = {_p(r, Action.READ) for r in _ALL_RESOURCES}


PERMISSIONS_BY_ROLE: dict[UserRole, set[Permission]] = {
    UserRole.ADMIN: _ADMIN,
    UserRole.DIRECTION: _DIRECTION,
    UserRole.CHARGE_AFFAIRES: _CHARGE_AFFAIRES,
    UserRole.CONDUCTEUR_TRAVAUX: _CONDUCTEUR,
    UserRole.LECTURE_SEULE: _LECTURE_SEULE,
}


def permissions_for(role: UserRole) -> set[Permission]:
    return PERMISSIONS_BY_ROLE.get(role, set())


def has_permission(role: UserRole, resource: Resource, action: Action) -> bool:
    """Vrai si le rôle dispose de la permission demandée.

    `MANAGE` implique `READ` et `WRITE` ; un `WRITE` implique l'accès en
    écriture mais pas l'administration.
    """
    perms = permissions_for(role)
    if Permission(resource, Action.MANAGE) in perms:
        return True
    if action in (Action.READ, Action.WRITE):
        return Permission(resource, action) in perms
    return Permission(resource, action) in perms
