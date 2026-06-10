"""Crawler de détection d'appels d'offres — BTP Agent Platform.

Workflow (SRS) : Crawler → Détection → Téléchargement → Analyse → Qualification.
Ce module fournit le squelette de détection ; la qualification GO/NO-GO est
déléguée à `btp.ao.qualify`.
"""

from __future__ import annotations

from dataclasses import dataclass

from btp.ao import QualificationResult, qualify

__all__ = ["DetectedTender", "score_relevance", "process"]


@dataclass
class DetectedTender:
    title: str
    url: str
    buyer: str | None = None
    text: str = ""


# Mots-clés sectoriels BTP pour le scoring de pertinence d'un AO détecté.
_KEYWORDS = (
    "btp", "bâtiment", "travaux", "génie civil", "gros œuvre", "vrd",
    "rénovation", "construction", "maçonnerie", "charpente",
)


def score_relevance(tender: DetectedTender) -> float:
    """Score [0..1] basé sur la densité de mots-clés sectoriels."""
    text = f"{tender.title} {tender.text}".lower()
    hits = sum(1 for kw in _KEYWORDS if kw in text)
    return min(1.0, hits / 4)


def process(tender: DetectedTender, *, threshold: float = 0.6) -> QualificationResult:
    """Détecte la pertinence puis qualifie l'AO en GO/NO-GO."""
    return qualify(score=score_relevance(tender), threshold=threshold)
