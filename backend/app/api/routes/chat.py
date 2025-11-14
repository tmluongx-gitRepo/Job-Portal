"""Chat streaming endpoint scaffolding."""

from __future__ import annotations

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.ai.chat.orchestrator import get_chat_orchestrator
from app.ai.chat.sessions import ChatSessionStore
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.websocket("/api/chat/ws")
async def chat_websocket(
    websocket: WebSocket, current_user: dict = Depends(get_current_user)
) -> None:
    """Authenticate the websocket and initialise a chat session.

    Real streaming logic will be added in subsequent phases. For now this echoes
    messages back through the orchestrator stub so we can exercise the plumbing.
    """
    await websocket.accept()
    session_store = ChatSessionStore()
    session = await session_store.get_or_create(
        user_id=current_user["id"], role=current_user["account_type"]
    )

    orchestrator = get_chat_orchestrator()

    try:
        await websocket.send_json(
            {
                "type": "info",
                "message": "Chat connection established",
                "session_id": session.session_id,
            }
        )

        while True:
            payload = await websocket.receive_json()
            message = payload.get("message")
            if not message:
                continue

            async for event in orchestrator.stream_response(
                message=message,
                user_context=current_user,
                session=session,
            ):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        pass
