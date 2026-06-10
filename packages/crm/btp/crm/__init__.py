"""Services métier CRM — clients, contacts, opportunités, interactions.

Couche de service au-dessus des modèles `btp.database.models.crm`.
"""

from __future__ import annotations

from btp.database.models import Client, Interaction, Opportunity
from sqlalchemy import select
from sqlalchemy.orm import Session

__all__ = ["create_client", "list_clients", "log_interaction", "list_opportunities"]


def create_client(session: Session, *, name: str, siret: str | None = None) -> Client:
    client = Client(name=name, siret=siret)
    session.add(client)
    session.flush()
    return client


def list_clients(session: Session) -> list[Client]:
    return list(session.scalars(select(Client).order_by(Client.name)))


def log_interaction(
    session: Session, *, client_id: str, summary: str, channel: str = "note"
) -> Interaction:
    interaction = Interaction(client_id=client_id, summary=summary, channel=channel)
    session.add(interaction)
    session.flush()
    return interaction


def list_opportunities(session: Session, *, client_id: str | None = None) -> list[Opportunity]:
    stmt = select(Opportunity)
    if client_id:
        stmt = stmt.where(Opportunity.client_id == client_id)
    return list(session.scalars(stmt))
