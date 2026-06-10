"""Tests du module CRM (clients, contacts, opportunités, interactions)."""

from __future__ import annotations


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_crm_full_flow(client, admin_token):
    h = _auth(admin_token)

    created = client.post(
        "/crm/clients",
        json={"name": "Mairie de Lyon", "siret": "21690123400015"},
        headers=h,
    )
    assert created.status_code == 201, created.text
    cid = created.json()["id"]

    assert any(c["id"] == cid for c in client.get("/crm/clients", headers=h).json())

    contact = client.post(
        f"/crm/clients/{cid}/contacts",
        json={"full_name": "Jean Dupont", "role": "Acheteur", "email": "jd@lyon.fr"},
        headers=h,
    )
    assert contact.status_code == 201
    contacts = client.get(f"/crm/clients/{cid}/contacts", headers=h).json()
    assert contacts[0]["full_name"] == "Jean Dupont"

    opp = client.post(
        f"/crm/clients/{cid}/opportunities",
        json={"title": "Rénovation école", "amount": 250000},
        headers=h,
    )
    assert opp.status_code == 201
    assert opp.json()["stage"] == "nouvelle"

    inter = client.post(
        f"/crm/clients/{cid}/interactions",
        json={"summary": "Appel de cadrage", "channel": "tel"},
        headers=h,
    )
    assert inter.status_code == 201
    assert client.get(f"/crm/clients/{cid}/interactions", headers=h).json()[0]["channel"] == "tel"


def test_crm_requires_existing_client(client, admin_token):
    resp = client.post(
        "/crm/clients/does-not-exist/contacts",
        json={"full_name": "X"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 404
