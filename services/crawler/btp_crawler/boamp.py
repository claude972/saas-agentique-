"""Source réelle d'appels d'offres : BOAMP (open data).

Le BOAMP (Bulletin Officiel des Annonces de Marchés Publics) publie les avis de
marchés publics français. Le jeu de données est exposé via l'API Opendatasoft
(Explore v2). On interroge par mots-clés, on convertit les enregistrements en
`DetectedTender`, puis `process()` (module parent) score et qualifie.

La fonction de requête HTTP est injectable (`fetch`) afin de tester le parsing
sans réseau.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from btp_crawler import DetectedTender

BOAMP_API = (
    "https://boamp-datadila.opendatasoft.com/api/explore/v2.1/"
    "catalog/datasets/boamp/records"
)


def _default_fetch(url: str, params: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover
    import httpx

    resp = httpx.get(url, params=params, timeout=20.0)
    resp.raise_for_status()
    return resp.json()


def parse_records(payload: dict[str, Any]) -> list[DetectedTender]:
    """Convertit la réponse Opendatasoft en `DetectedTender`."""
    tenders: list[DetectedTender] = []
    for record in payload.get("results", []):
        title = record.get("objet") or record.get("intitule") or "AO sans intitulé"
        idweb = record.get("idweb") or record.get("id")
        url = f"https://www.boamp.fr/avis/detail/{idweb}" if idweb else ""
        tenders.append(
            DetectedTender(
                title=str(title),
                url=url,
                buyer=record.get("nomacheteur") or record.get("acheteur"),
                text=" ".join(
                    str(record.get(k, ""))
                    for k in ("objet", "descripteur_libelle", "famille_libelle")
                ),
            )
        )
    return tenders


def search(
    keywords: str,
    *,
    limit: int = 20,
    fetch: Callable[[str, dict[str, Any]], dict[str, Any]] = _default_fetch,
) -> list[DetectedTender]:
    """Recherche des AO BOAMP par mots-clés et retourne les avis détectés."""
    params = {"where": f'"{keywords}"', "limit": limit, "order_by": "dateparution desc"}
    payload = fetch(BOAMP_API, params)
    return parse_records(payload)
