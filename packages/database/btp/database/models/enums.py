"""Énumérations métier partagées."""

from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DIRECTION = "direction"
    CHARGE_AFFAIRES = "charge_affaires"
    CONDUCTEUR_TRAVAUX = "conducteur_travaux"
    LECTURE_SEULE = "lecture_seule"


class ProjectStatus(str, enum.Enum):
    PROSPECT = "prospect"
    ETUDE = "etude"
    EN_COURS = "en_cours"
    SUSPENDU = "suspendu"
    TERMINE = "termine"
    ARCHIVE = "archive"


class DocumentKind(str, enum.Enum):
    CCTP = "cctp"
    CCAP = "ccap"
    BPU = "bpu"
    DPGF = "dpgf"
    PLAN = "plan"
    DEVIS = "devis"
    PHOTO = "photo"
    COMPTE_RENDU = "compte_rendu"
    AUTRE = "autre"


class QuoteStatus(str, enum.Enum):
    BROUILLON = "brouillon"
    EN_REVISION = "en_revision"
    ENVOYE = "envoye"
    ACCEPTE = "accepte"
    REFUSE = "refuse"


class TenderDecision(str, enum.Enum):
    A_QUALIFIER = "a_qualifier"
    GO = "go"
    NO_GO = "no_go"


class ReportKind(str, enum.Enum):
    CHANTIER = "chantier"
    VISITE = "visite"
    REUNION = "reunion"
    RESERVE = "reserve"


class OpportunityStage(str, enum.Enum):
    NOUVELLE = "nouvelle"
    QUALIFIEE = "qualifiee"
    PROPOSITION = "proposition"
    NEGOCIATION = "negociation"
    GAGNEE = "gagnee"
    PERDUE = "perdue"
