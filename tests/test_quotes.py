"""Tests devis (Sprint 5) : agent JSON, persistance, PDF, API."""

from __future__ import annotations

import io

from btp.agents._json import extract_json
from btp.quotes import QuoteDraft, QuoteLineDraft, render_quote_pdf


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_extract_json_handles_markdown_fence():
    text = '```json\n{"lignes": [{"designation": "Béton", "quantite": 3}]}\n```'
    data = extract_json(text)
    assert data["lignes"][0]["designation"] == "Béton"


def test_render_quote_pdf_produces_pdf_bytes():
    draft = QuoteDraft(
        reference="DEV-TEST01",
        lines=[
            QuoteLineDraft("Béton armé", "m3", 12, 180.0),
            QuoteLineDraft("Coffrage", "m2", 40, 35.0),
        ],
    )
    assert draft.total_ht == 12 * 180.0 + 40 * 35.0
    pdf = render_quote_pdf(draft, project_name="Gymnase", client_name="Mairie")
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 500


def test_quote_api_flow(client, admin_token):
    pid = client.post(
        "/projects", json={"name": "Chantier devis"}, headers=_auth(admin_token)
    ).json()["id"]

    gen = client.post(
        f"/projects/{pid}/quotes/generate",
        json={"description": "Dalle béton 30 m2, hauteur 0,2 m"},
        headers=_auth(admin_token),
    )
    assert gen.status_code == 201, gen.text
    quote = gen.json()
    assert quote["reference"].startswith("DEV-")
    assert quote["status"] == "brouillon"
    qid = quote["id"]

    # Archivage PDF
    built = client.post(f"/quotes/{qid}/pdf", headers=_auth(admin_token))
    assert built.status_code == 200
    assert built.json()["pdf_s3_key"]

    pdf = client.get(f"/quotes/{qid}/pdf", headers=_auth(admin_token))
    assert pdf.status_code == 200
    assert pdf.content[:5] == b"%PDF-"


def test_document_analyze_extracts_text(client, admin_token):
    pid = client.post(
        "/projects", json={"name": "Chantier docs"}, headers=_auth(admin_token)
    ).json()["id"]

    content = b"CCTP lot 2 - cloisons placo BA13"
    did = client.post(
        f"/projects/{pid}/documents",
        files={"file": ("cctp.txt", io.BytesIO(content), "text/plain")},
        headers=_auth(admin_token),
    ).json()["id"]

    analyzed = client.post(f"/documents/{did}/analyze", headers=_auth(admin_token))
    assert analyzed.status_code == 200, analyzed.text
    assert analyzed.json()["ocr_text"] == content.decode()
