"""Schémas Pydantic d'entrée/sortie de l'API."""

from __future__ import annotations

from datetime import datetime

from btp.database.models.enums import ProjectStatus, ReportKind, UserRole
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Auth ---------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Users --------------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    role: UserRole = UserRole.LECTURE_SEULE


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    # Sortie : on fait confiance à la valeur stockée (pas de re-validation,
    # ce qui autorise des domaines internes type *.local).
    email: str
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime


# --- Projects -----------------------------------------------------------------
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    client_id: str | None = None
    status: ProjectStatus = ProjectStatus.PROSPECT


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    client_id: str | None = None
    status: ProjectStatus | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    status: ProjectStatus
    client_id: str | None
    created_at: datetime
    updated_at: datetime


# --- Agents -------------------------------------------------------------------
class AgentInfo(BaseModel):
    name: str
    description: str


class SupervisorRequest(BaseModel):
    prompt: str
    project_id: str | None = None
    inputs: dict[str, object] = Field(default_factory=dict)


# --- Chat ---------------------------------------------------------------------
class ConversationCreate(BaseModel):
    title: str | None = None


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    title: str | None
    created_at: datetime


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    created_at: datetime


class ChatPostRequest(BaseModel):
    content: str = Field(min_length=1)


class ChatPostResponse(BaseModel):
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut
    plan: dict[str, object]


# --- Documents ----------------------------------------------------------------
class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    filename: str
    mime_type: str | None
    kind: str
    version: int
    created_at: datetime


class DocumentDetail(DocumentOut):
    ocr_text: str | None = None


# --- Quotes (devis) -----------------------------------------------------------
class QuoteGenerateRequest(BaseModel):
    description: str = Field(min_length=1)


class QuoteLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: int
    designation: str
    unit: str
    quantity: float
    unit_price: float


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    reference: str
    status: str
    total_ht: float
    pdf_s3_key: str | None
    created_at: datetime


class QuoteDetail(QuoteOut):
    lines: list[QuoteLineOut] = Field(default_factory=list)


# --- Photos (chantier) --------------------------------------------------------
class PhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    caption: str | None
    analysis: str | None
    created_at: datetime


# --- Reports (comptes-rendus) -------------------------------------------------
class ReportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    kind: ReportKind = ReportKind.CHANTIER
    notes: str | None = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    kind: ReportKind
    title: str
    content: str | None
    validated: bool
    created_at: datetime


# --- Appels d'offres (AO / tenders) -------------------------------------------
class TenderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    source_url: str | None = None
    buyer: str | None = None


class TenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    title: str
    source_url: str | None
    buyer: str | None
    decision: str
    qualification: str | None
    created_at: datetime


class TenderQualifyRequest(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(default=0.6, ge=0.0, le=1.0)


class ConsultationAnalyzeRequest(BaseModel):
    document_ids: list[str] = Field(min_length=1)


class TenderResponseOut(BaseModel):
    document_id: str
    memoire_technique: str
