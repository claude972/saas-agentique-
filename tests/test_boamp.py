"""Tests crawler BOAMP : parsing hors-ligne + endpoint de détection."""

from __future__ import annotations

from btp_crawler import DetectedTender, process
from btp_crawler.boamp import parse_records, search

_FAKE_PAYLOAD = {
    "results": [
        {
            "idweb": "25-12345",
            "objet": "Travaux de gros œuvre et maçonnerie - construction d'un gymnase",
            "nomacheteur": "Ville de Lyon",
            "descripteur_libelle": "bâtiment",
        },
        {
            "idweb": "25-99999",
            "objet": "Fourniture de mobilier de bureau",
            "nomacheteur": "Conseil départemental",
        },
    ]
}


def _fake_fetch(url, params):
    return _FAKE_PAYLOAD


def test_parse_records():
    tenders = parse_records(_FAKE_PAYLOAD)
    assert len(tenders) == 2
    assert tenders[0].buyer == "Ville de Lyon"
    assert "gymnase" in tenders[0].text.lower()
    assert tenders[0].url.endswith("25-12345")


def test_search_with_injected_fetch_and_qualification():
    tenders = search("gymnase", fetch=_fake_fetch)
    # L'AO BTP doit être GO, le mobilier NO-GO (scoring sectoriel).
    go = process(tenders[0])
    nogo = process(tenders[1])
    assert go.decision.value == "go"
    assert nogo.decision.value == "no_go"


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_detect_endpoint(client, admin_token, monkeypatch):
    # On évite l'appel réseau en stubbant la recherche BOAMP.
    import btp_api.routers.ao as ao_router

    def fake_search(keywords, *, limit=10):
        return [
            DetectedTender(
                title="Réhabilitation thermique bâtiment", url="http://x", buyer="Mairie",
                text="bâtiment rénovation travaux",
            )
        ]

    monkeypatch.setattr(ao_router, "boamp_search", fake_search)

    pid = client.post(
        "/projects", json={"name": "Veille AO"}, headers=_auth(admin_token)
    ).json()["id"]
    resp = client.post(
        f"/projects/{pid}/tenders/detect",
        json={"keywords": "bâtiment"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert len(body) == 1
    assert body[0]["decision"] == "go"
