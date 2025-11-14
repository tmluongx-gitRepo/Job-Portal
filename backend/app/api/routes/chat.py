"""Chat streaming endpoint scaffolding."""

from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.ai.chat.sessions import ChatSessionStore
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.websocket("/api/chat/ws")
async def chat_websocket(
    websocket: WebSocket, current_user: dict = Depends(get_current_user)
) -> None:
    """Authenticate the websocket and initialise a chat session.

    Real streaming logic will be added in subsequent phases. For now this just
    accepts the connection, creates/loads a session, and immediately closes the
    socket to confirm wiring.
    """
    await websocket.accept()
    session_store = ChatSessionStore()
    session = await session_store.get_or_create(
        user_id=current_user["id"], role=current_user["account_type"]
    )

    try:
        await websocket.send_json(
            {
                "type": "info",
                "message": "Chat connection established",
                "session_id": session.session_id,
            }
        )
        await websocket.close()
    except WebSocketDisconnect:
        # Client disconnected before we closed explicitly; nothing else to do
        pass
