"""Tests d'intégration : chat persistant (Sprint 3) et documents (Sprint 2)."""

from __future__ import annotations

import io


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _new_project(client, token: str) -> str:
    resp = client.post(
        "/projects", json={"name": "Projet test chat/docs"}, headers=_auth(token)
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_chat_flow_persists_history(client, admin_token):
    pid = _new_project(client, admin_token)

    conv = client.post(
        f"/projects/{pid}/conversations",
        json={"title": "Étude devis"},
        headers=_auth(admin_token),
    )
    assert conv.status_code == 201, conv.text
    cid = conv.json()["id"]

    # Premier message → déclenche le supervisor (mock hors-ligne).
    first = client.post(
        f"/conversations/{cid}/messages",
        json={"content": "Analyse cette photo et prépare un devis"},
        headers=_auth(admin_token),
    )
    assert first.status_code == 200, first.text
    body = first.json()
    assert body["user_message"]["role"] == "user"
    assert body["assistant_message"]["role"] == "assistant"
    assert "PhotoAgent" in body["plan"]["agents"]

    # Second message → l'historique doit déjà contenir 2 messages.
    client.post(
        f"/conversations/{cid}/messages",
        json={"content": "Rédige un compte-rendu de réunion"},
        headers=_auth(admin_token),
    )

    messages = client.get(
        f"/conversations/{cid}/messages", headers=_auth(admin_token)
    ).json()
    # 2 tours user + 2 réponses assistant = 4 messages persistés.
    assert len(messages) == 4
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]


def test_document_upload_and_download(client, admin_token):
    pid = _new_project(client, admin_token)

    content = b"CCTP - lot gros oeuvre - beton arme"
    resp = client.post(
        f"/projects/{pid}/documents",
        files={"file": ("cctp.txt", io.BytesIO(content), "text/plain")},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 201, resp.text
    doc = resp.json()
    assert doc["filename"] == "cctp.txt"
    assert doc["mime_type"] == "text/plain"
    did = doc["id"]

    listed = client.get(f"/projects/{pid}/documents", headers=_auth(admin_token)).json()
    assert any(d["id"] == did for d in listed)

    downloaded = client.get(f"/documents/{did}/download", headers=_auth(admin_token))
    assert downloaded.status_code == 200
    assert downloaded.content == content
