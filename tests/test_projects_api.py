"""Tests d'intégration de l'API projets (auth + RBAC + CRUD)."""

from __future__ import annotations


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_projects_require_auth(client):
    assert client.get("/projects").status_code == 401


def test_project_crud(client, admin_token):
    # Création
    resp = client.post(
        "/projects",
        json={"name": "Réhabilitation Gymnase", "description": "Lot gros œuvre"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 201, resp.text
    project = resp.json()
    assert project["name"] == "Réhabilitation Gymnase"
    assert project["status"] == "prospect"
    pid = project["id"]

    # Lecture
    assert client.get(f"/projects/{pid}", headers=_auth(admin_token)).status_code == 200

    # Mise à jour
    resp = client.patch(
        f"/projects/{pid}", json={"status": "en_cours"}, headers=_auth(admin_token)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "en_cours"

    # Liste
    listed = client.get("/projects", headers=_auth(admin_token)).json()
    assert any(p["id"] == pid for p in listed)

    # Suppression
    assert client.delete(f"/projects/{pid}", headers=_auth(admin_token)).status_code == 204
    assert client.get(f"/projects/{pid}", headers=_auth(admin_token)).status_code == 404


def test_readonly_cannot_write(client, admin_token):
    # L'admin crée un utilisateur en lecture seule…
    created = client.post(
        "/users",
        json={"email": "ro@example.com", "password": "password123", "role": "lecture_seule"},
        headers=_auth(admin_token),
    )
    assert created.status_code == 201, created.text

    ro_token = client.post(
        "/auth/login", data={"username": "ro@example.com", "password": "password123"}
    ).json()["access_token"]

    # … qui peut lire mais pas écrire (RBAC appliqué côté API).
    assert client.get("/projects", headers=_auth(ro_token)).status_code == 200
    forbidden = client.post("/projects", json={"name": "X"}, headers=_auth(ro_token))
    assert forbidden.status_code == 403
