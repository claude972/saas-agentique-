"""CLI d'administration : initialisation DB et création d'un compte admin."""

from __future__ import annotations

import typer
from btp.auth import hash_password
from btp.database import init_db as _init_db
from btp.database import session_scope
from btp.database.models import User
from btp.database.models.enums import UserRole
from sqlalchemy import select

app = typer.Typer(help="Administration — BTP Agent Platform")


@app.command("init-db")
def init_db() -> None:
    """Crée toutes les tables de la base."""
    _init_db()
    typer.secho("Base de données initialisée.", fg=typer.colors.GREEN)


@app.command("create-admin")
def create_admin(
    email: str = typer.Option(..., help="Email de l'administrateur"),
    password: str = typer.Option(..., help="Mot de passe (min 8 caractères)"),
    full_name: str = typer.Option("Administrateur", help="Nom complet"),
) -> None:
    """Crée (ou réactive) un compte administrateur."""
    _init_db()
    with session_scope() as session:
        existing = session.scalar(select(User).where(User.email == email))
        if existing is not None:
            typer.secho(f"L'utilisateur {email} existe déjà.", fg=typer.colors.YELLOW)
            raise typer.Exit(code=1)
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=UserRole.ADMIN,
        )
        session.add(user)
    typer.secho(f"Administrateur {email} créé.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
