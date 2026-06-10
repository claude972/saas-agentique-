"""Tests workflow appels d'offres (Sprints 7-8-9)."""

from __future__ import annotations

import io


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _project(client, token: str) -> str:
    return client.post(
        "/projects", json={"name": "Projet AO"}, headers=_auth(token)
    ).json()["id"]


def test_tender_qualification_go(client, admin_token):
    pid = _project(client, admin_token)
    tender = client.post(
        f"/projects/{pid}/tenders",
        json={"title": "Réfection toiture école", "buyer": "Mairie", "source_url": "http://ao"},
        headers=_auth(admin_token),
    )
    assert tender.status_code == 201, tender.text
    tid = tender.json()["id"]
    assert tender.json()["decision"] == "a_qualifier"

    q = client.post(
        f"/tenders/{tid}/qualify", json={"score": 0.8}, headers=_auth(admin_token)
    )
    assert q.status_code == 200
    assert q.json()["decision"] == "go"

    no = client.post(
        f"/tenders/{tid}/qualify", json={"score": 0.2}, headers=_auth(admin_token)
    )
    assert no.json()["decision"] == "no_go"


def test_consultation_analysis(client, admin_token):
    pid = _project(client, admin_token)
    did = client.post(
        f"/projects/{pid}/documents",
        files={"file": ("cctp.txt", io.BytesIO(b"Exigence: beton C25/30"), "text/plain")},
        headers=_auth(admin_token),
    ).json()["id"]
    client.post(f"/documents/{did}/analyze", headers=_auth(admin_token))  # remplit ocr_text

    resp = client.post(
        f"/projects/{pid}/consultation/analyze",
        json={"document_ids": [did]},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 200, resp.text
    assert "synthese" in resp.json()


def test_tender_response_archived_as_document(client, admin_token):
    pid = _project(client, admin_token)
    tid = client.post(
        f"/projects/{pid}/tenders",
        json={"title": "Construction gymnase"},
        headers=_auth(admin_token),
    ).json()["id"]

    resp = client.post(f"/tenders/{tid}/respond", headers=_auth(admin_token))
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["memoire_technique"]

    # La mémoire technique est archivée comme document du projet.
    docs = client.get(f"/projects/{pid}/documents", headers=_auth(admin_token)).json()
    assert any(d["id"] == body["document_id"] for d in docs)
