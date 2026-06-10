"""Module CRM : clients, contacts, opportunités, interactions.

S'appuie sur la couche de service `btp.crm` au-dessus des modèles ORM.
"""

from __future__ import annotations

from typing import Annotated

from btp.auth.rbac import Action, Resource
from btp.crm import create_client, list_clients
from btp.database.models import Client, Contact, Interaction, Opportunity, User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import (
    ClientCreate,
    ClientOut,
    ContactCreate,
    ContactOut,
    InteractionCreate,
    InteractionOut,
    OpportunityCreate,
    OpportunityOut,
)

router = APIRouter(prefix="/crm", tags=["crm"])

_read = Annotated[User, Depends(require_permission(Resource.CRM, Action.READ))]
_write = Annotated[User, Depends(require_permission(Resource.CRM, Action.WRITE))]


def _client_or_404(db: DbSession, client_id: str) -> Client:
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")
    return client


# --- Clients ------------------------------------------------------------------
@router.post("/clients", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def add_client(payload: ClientCreate, db: DbSession, _: _write) -> Client:
    client = create_client(db, name=payload.name, siret=payload.siret)
    client.address = payload.address
    db.flush()
    return client


@router.get("/clients", response_model=list[ClientOut])
def get_clients(db: DbSession, _: _read) -> list[Client]:
    return list_clients(db)


# --- Contacts -----------------------------------------------------------------
@router.post(
    "/clients/{client_id}/contacts",
    response_model=ContactOut,
    status_code=status.HTTP_201_CREATED,
)
def add_contact(
    client_id: str, payload: ContactCreate, db: DbSession, _: _write
) -> Contact:
    _client_or_404(db, client_id)
    contact = Contact(client_id=client_id, **payload.model_dump())
    db.add(contact)
    db.flush()
    return contact


@router.get("/clients/{client_id}/contacts", response_model=list[ContactOut])
def get_contacts(client_id: str, db: DbSession, _: _read) -> list[Contact]:
    return list(db.scalars(select(Contact).where(Contact.client_id == client_id)))


# --- Opportunités -------------------------------------------------------------
@router.post(
    "/clients/{client_id}/opportunities",
    response_model=OpportunityOut,
    status_code=status.HTTP_201_CREATED,
)
def add_opportunity(
    client_id: str, payload: OpportunityCreate, db: DbSession, _: _write
) -> Opportunity:
    _client_or_404(db, client_id)
    opportunity = Opportunity(client_id=client_id, **payload.model_dump())
    db.add(opportunity)
    db.flush()
    return opportunity


@router.get("/clients/{client_id}/opportunities", response_model=list[OpportunityOut])
def get_opportunities(client_id: str, db: DbSession, _: _read) -> list[Opportunity]:
    return list(db.scalars(select(Opportunity).where(Opportunity.client_id == client_id)))


# --- Interactions -------------------------------------------------------------
@router.post(
    "/clients/{client_id}/interactions",
    response_model=InteractionOut,
    status_code=status.HTTP_201_CREATED,
)
def add_interaction(
    client_id: str, payload: InteractionCreate, db: DbSession, _: _write
) -> Interaction:
    _client_or_404(db, client_id)
    interaction = Interaction(client_id=client_id, **payload.model_dump())
    db.add(interaction)
    db.flush()
    return interaction


@router.get("/clients/{client_id}/interactions", response_model=list[InteractionOut])
def get_interactions(client_id: str, db: DbSession, _: _read) -> list[Interaction]:
    stmt = (
        select(Interaction)
        .where(Interaction.client_id == client_id)
        .order_by(Interaction.created_at.desc())
    )
    return list(db.scalars(stmt))
