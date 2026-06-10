"""Chat agentique par projet, avec mémoire persistante (Sprint 3).

Chaque conversation est rattachée à un projet. Un message utilisateur déclenche
le `SupervisorAgent`, dont la synthèse est persistée comme réponse assistant —
l'historique complet est rejoué dans le contexte à chaque tour.
"""

from __future__ import annotations

import json
from typing import Annotated

from btp.agents import AgentContext, SupervisorAgent
from btp.auth.rbac import Action, Resource
from btp.database.models import ChatMessage, Conversation, Project, User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from btp_api.deps import DbSession, require_permission
from btp_api.schemas import (
    ChatMessageOut,
    ChatPostRequest,
    ChatPostResponse,
    ConversationCreate,
    ConversationOut,
)

router = APIRouter(tags=["chat"])

_read = Annotated[User, Depends(require_permission(Resource.PROJECTS, Action.READ))]
_write = Annotated[User, Depends(require_permission(Resource.PROJECTS, Action.WRITE))]


def _conversation_or_404(db: DbSession, conversation_id: str) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation introuvable"
        )
    return conversation


@router.post(
    "/projects/{project_id}/conversations",
    response_model=ConversationOut,
    status_code=status.HTTP_201_CREATED,
    tags=["chat"],
)
def create_conversation(
    project_id: str, payload: ConversationCreate, db: DbSession, _: _write
) -> Conversation:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    conversation = Conversation(project_id=project_id, title=payload.title)
    db.add(conversation)
    db.flush()
    return conversation


@router.get(
    "/projects/{project_id}/conversations",
    response_model=list[ConversationOut],
    tags=["chat"],
)
def list_conversations(project_id: str, db: DbSession, _: _read) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .order_by(Conversation.created_at.desc())
    )
    return list(db.scalars(stmt))


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[ChatMessageOut],
    tags=["chat"],
)
def list_messages(conversation_id: str, db: DbSession, _: _read) -> list[ChatMessage]:
    conversation = _conversation_or_404(db, conversation_id)
    return list(conversation.messages)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatPostResponse,
    tags=["chat"],
)
async def post_message(
    conversation_id: str, payload: ChatPostRequest, db: DbSession, _: _write
) -> ChatPostResponse:
    conversation = _conversation_or_404(db, conversation_id)

    # Mémoire persistante : on rejoue l'historique dans le contexte de l'agent.
    history = [{"role": m.role, "content": m.content} for m in conversation.messages]

    user_msg = ChatMessage(conversation_id=conversation.id, role="user", content=payload.content)
    db.add(user_msg)
    db.flush()

    supervisor = SupervisorAgent()
    result = await supervisor.run(
        AgentContext(
            project_id=conversation.project_id,
            prompt=payload.content,
            history=history,
        )
    )

    summary = str(result.get("summary", ""))
    assistant_msg = ChatMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=summary,
        meta=json.dumps(result.get("plan", {})),
    )
    db.add(assistant_msg)
    db.flush()

    return ChatPostResponse(
        user_message=ChatMessageOut.model_validate(user_msg),
        assistant_message=ChatMessageOut.model_validate(assistant_msg),
        plan=result.get("plan", {}),  # type: ignore[arg-type]
    )
