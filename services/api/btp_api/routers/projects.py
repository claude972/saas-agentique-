"""CRUD projets, protégé par les permissions projects:read / projects:write."""

from __future__ import annotations

from typing import Annotated

from btp.auth.rbac import Action, Resource
from btp.database.models import Project, User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])

_read = Annotated[User, Depends(require_permission(Resource.PROJECTS, Action.READ))]
_write = Annotated[User, Depends(require_permission(Resource.PROJECTS, Action.WRITE))]


def _get_or_404(db: DbSession, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(db: DbSession, _: _read) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.created_at.desc())))


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: DbSession, _: _write) -> Project:
    project = Project(
        name=payload.name,
        description=payload.description,
        client_id=payload.client_id,
        status=payload.status,
    )
    db.add(project)
    db.flush()
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: DbSession, _: _read) -> Project:
    return _get_or_404(db, project_id)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str, payload: ProjectUpdate, db: DbSession, _: _write
) -> Project:
    project = _get_or_404(db, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.flush()
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: DbSession, _: _write) -> None:
    project = _get_or_404(db, project_id)
    db.delete(project)
