"""Téléversement et gestion documentaire (Sprint 2).

Stockage via l'abstraction `btp.documents` (disque en dev, S3 en prod). Le
classement automatique / OCR (DocumentAgent) viendra enrichir ces enregistrements.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from btp.agents import AgentContext, get_agent
from btp.auth.rbac import Action, Resource
from btp.database.models import Document, Project, User
from btp.database.models.enums import DocumentKind
from btp.documents import get_object_store
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import DocumentDetail, DocumentOut

router = APIRouter(tags=["documents"])

_read = Annotated[User, Depends(require_permission(Resource.DOCUMENTS, Action.READ))]
_write = Annotated[User, Depends(require_permission(Resource.DOCUMENTS, Action.WRITE))]


@router.post(
    "/projects/{project_id}/documents",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    project_id: str,
    db: DbSession,
    _: _write,
    file: Annotated[UploadFile, File()],
) -> Document:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")

    data = await file.read()
    key = f"projects/{project_id}/{uuid.uuid4()}/{file.filename}"
    get_object_store().put(key, data, content_type=file.content_type)

    document = Document(
        project_id=project_id,
        filename=file.filename or "document",
        s3_key=key,
        mime_type=file.content_type,
    )
    db.add(document)
    db.flush()
    return document


@router.get("/projects/{project_id}/documents", response_model=list[DocumentOut])
def list_documents(project_id: str, db: DbSession, _: _read) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at.desc())
    )
    return list(db.scalars(stmt))


@router.post("/documents/{document_id}/analyze", response_model=DocumentDetail)
async def analyze_document(document_id: str, db: DbSession, _: _write) -> Document:
    """Extrait le texte (OCR) et classe le document via le DocumentAgent.

    Pour les fichiers texte, l'extraction est directe ; pour les autres, le
    DocumentAgent (LLM/vision) est sollicité — repli gracieux hors-ligne.
    """
    document = db.get(Document, document_id)
    if document is None or not document.s3_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")

    data = get_object_store().get(document.s3_key)
    mime = (document.mime_type or "").lower()

    if mime.startswith("text/") or mime in ("application/json", "application/xml"):
        document.ocr_text = data.decode("utf-8", errors="replace")
    else:
        agent = get_agent("DocumentAgent")
        result = await agent.run(
            AgentContext(prompt=f"Document: {document.filename}", inputs={"images": [data]})
        )
        document.ocr_text = str(result.output.get("ocr_text") or result.summary)
        kind = result.output.get("kind")
        if isinstance(kind, str):
            try:
                document.kind = DocumentKind(kind)
            except ValueError:
                pass

    db.flush()
    return document


@router.get("/documents/{document_id}/download")
def download_document(document_id: str, db: DbSession, _: _read) -> Response:
    document = db.get(Document, document_id)
    if document is None or not document.s3_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    data = get_object_store().get(document.s3_key)
    return Response(
        content=data,
        media_type=document.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )
