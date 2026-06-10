"""Modèles ORM de la plateforme BTP."""

from btp.database.models.activity import ActivityLog
from btp.database.models.chat import ChatMessage, Conversation
from btp.database.models.crm import Client, Contact, Interaction, Opportunity
from btp.database.models.document import Document, Photo
from btp.database.models.enums import (
    DocumentKind,
    OpportunityStage,
    ProjectStatus,
    QuoteStatus,
    ReportKind,
    TenderDecision,
    UserRole,
)
from btp.database.models.project import Project
from btp.database.models.quote import Quote, QuoteLine
from btp.database.models.report import Report
from btp.database.models.tender import Tender
from btp.database.models.user import User

__all__ = [
    # enums
    "UserRole",
    "ProjectStatus",
    "DocumentKind",
    "QuoteStatus",
    "TenderDecision",
    "ReportKind",
    "OpportunityStage",
    # models
    "User",
    "Project",
    "Client",
    "Contact",
    "Opportunity",
    "Interaction",
    "Document",
    "Photo",
    "Quote",
    "QuoteLine",
    "Tender",
    "Report",
    "Conversation",
    "ChatMessage",
    "ActivityLog",
]
