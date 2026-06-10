"""Photos de chantier (Sprint 4) : upload + analyse PhotoAgent.

Workflow (SRS) : Photo → PhotoAgent → description / ouvrages / quantités /
anomalies. Le résultat structuré est archivé sur la photo (champ `analysis`).
"""

from __future__ import annotations

import json
import uuid
from typing import Annotated

from btp.agents import AgentContext, get_agent
from btp.auth.rbac import Action, Resource
from btp.database.models import Photo, Project, User
from btp.documents import get_object_store
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import PhotoOut

router = APIRouter(tags=["photos"])

_read = Annotated[User, Depends(require_permission(Resource.CHANTIER, Action.READ))]
_write = Annotated[User, Depends(require_permission(Resource.CHANTIER, Action.WRITE))]


def _photo_or_404(db: DbSession, photo_id: str) -> Photo:
    photo = db.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo introuvable")
    return photo


@router.post(
    "/projects/{project_id}/photos",
    response_model=PhotoOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
    project_id: str,
    db: DbSession,
    _: _write,
    file: Annotated[UploadFile, File()],
    caption: Annotated[str | None, Form()] = None,
) -> Photo:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")

    data = await file.read()
    key = f"projects/{project_id}/photos/{uuid.uuid4()}/{file.filename}"
    get_object_store().put(key, data, content_type=file.content_type)

    photo = Photo(project_id=project_id, s3_key=key, caption=caption)
    db.add(photo)
    db.flush()
    return photo


@router.get("/projects/{project_id}/photos", response_model=list[PhotoOut])
def list_photos(project_id: str, db: DbSession, _: _read) -> list[Photo]:
    stmt = (
        select(Photo)
        .where(Photo.project_id == project_id)
        .order_by(Photo.created_at.desc())
    )
    return list(db.scalars(stmt))


@router.post("/photos/{photo_id}/analyze", response_model=PhotoOut)
async def analyze_photo(photo_id: str, db: DbSession, _: _write) -> Photo:
    photo = _photo_or_404(db, photo_id)
    data = get_object_store().get(photo.s3_key)
    agent = get_agent("PhotoAgent")
    result = await agent.run(
        AgentContext(
            project_id=photo.project_id,
            prompt=photo.caption or "",
            inputs={"images": [data]},
        )
    )
    photo.analysis = json.dumps(result.output, ensure_ascii=False)
    db.flush()
    return photo
