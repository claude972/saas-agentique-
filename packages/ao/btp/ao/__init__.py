"""Services métier appels d'offres (AO).

Workflow (SRS) : Crawler → Détection → Téléchargement → Analyse → Qualification
→ GO / NO-GO → TenderAgent → Dossier final.
"""

from __future__ import annotations

from dataclasses import dataclass

from btp.database.models.enums import TenderDecision

__all__ = ["QualificationResult", "qualify"]


@dataclass
class QualificationResult:
    decision: TenderDecision
    score: float
    rationale: str


def qualify(*, score: float, threshold: float = 0.6) -> QualificationResult:
    """Décision GO/NO-GO à partir d'un score de pertinence (0..1).

    L'analyse fine (lecture des pièces, capacité, marges) sera produite par le
    `ConsultationAgent` ; cette fonction matérialise la règle de décision.
    """
    if score >= threshold:
        decision = TenderDecision.GO
        rationale = f"Score {score:.2f} ≥ seuil {threshold:.2f} → GO"
    else:
        decision = TenderDecision.NO_GO
        rationale = f"Score {score:.2f} < seuil {threshold:.2f} → NO-GO"
    return QualificationResult(decision=decision, score=score, rationale=rationale)
