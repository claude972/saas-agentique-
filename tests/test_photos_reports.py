"""Tests photos (Sprint 4) et comptes-rendus (Sprint 6)."""

from __future__ import annotations

import io


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _project(client, token: str) -> str:
    return client.post(
        "/projects", json={"name": "Chantier photos/CR"}, headers=_auth(token)
    ).json()["id"]


def test_photo_upload_and_analyze(client, admin_token):
    pid = _project(client, admin_token)
    img = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32  # entête PNG + données factices

    up = client.post(
        f"/projects/{pid}/photos",
        files={"file": ("chantier.png", io.BytesIO(img), "image/png")},
        data={"caption": "Mur pignon"},
        headers=_auth(admin_token),
    )
    assert up.status_code == 201, up.text
    photo_id = up.json()["id"]
    assert up.json()["caption"] == "Mur pignon"

    analyzed = client.post(f"/photos/{photo_id}/analyze", headers=_auth(admin_token))
    assert analyzed.status_code == 200, analyzed.text
    assert analyzed.json()["analysis"] is not None

    listed = client.get(f"/projects/{pid}/photos", headers=_auth(admin_token)).json()
    assert any(p["id"] == photo_id for p in listed)


def test_report_generate_and_validate(client, admin_token):
    pid = _project(client, admin_token)

    gen = client.post(
        f"/projects/{pid}/reports/generate",
        json={"title": "CR réunion n°3", "kind": "reunion", "notes": "Points abordés..."},
        headers=_auth(admin_token),
    )
    assert gen.status_code == 201, gen.text
    report = gen.json()
    assert report["kind"] == "reunion"
    assert report["validated"] is False
    assert report["content"]
    rid = report["id"]

    validated = client.post(f"/reports/{rid}/validate", headers=_auth(admin_token))
    assert validated.status_code == 200
    assert validated.json()["validated"] is True


def test_report_from_audio_requires_transcription(client, admin_token, monkeypatch):
    # Sans OPENAI_API_KEY, la transcription est indisponible → 503 explicite.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    pid = _project(client, admin_token)
    resp = client.post(
        f"/projects/{pid}/reports/from-audio",
        files={"file": ("note.webm", io.BytesIO(b"fake-audio"), "audio/webm")},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 503
