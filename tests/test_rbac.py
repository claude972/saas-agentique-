"""Tests de la matrice RBAC."""

from __future__ import annotations

from btp.auth.rbac import Action, Resource, has_permission
from btp.database.models.enums import UserRole


def test_admin_has_everything():
    for resource in Resource:
        for action in (Action.READ, Action.WRITE):
            assert has_permission(UserRole.ADMIN, resource, action)


def test_lecture_seule_is_read_only():
    assert has_permission(UserRole.LECTURE_SEULE, Resource.PROJECTS, Action.READ)
    assert not has_permission(UserRole.LECTURE_SEULE, Resource.PROJECTS, Action.WRITE)


def test_charge_affaires_scope():
    assert has_permission(UserRole.CHARGE_AFFAIRES, Resource.QUOTES, Action.WRITE)
    assert has_permission(UserRole.CHARGE_AFFAIRES, Resource.AO, Action.WRITE)
    # Pas d'accès à la gestion des utilisateurs.
    assert not has_permission(UserRole.CHARGE_AFFAIRES, Resource.USERS, Action.READ)


def test_conducteur_scope():
    assert has_permission(UserRole.CONDUCTEUR_TRAVAUX, Resource.CHANTIER, Action.WRITE)
    assert has_permission(UserRole.CONDUCTEUR_TRAVAUX, Resource.REPORTS, Action.WRITE)
    assert not has_permission(UserRole.CONDUCTEUR_TRAVAUX, Resource.QUOTES, Action.WRITE)
