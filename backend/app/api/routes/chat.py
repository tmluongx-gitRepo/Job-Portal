"""Chat streaming endpoint scaffolding."""

from __future__ import annotations

import time
from collections import deque

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.ai.chat.constants import ChatEventType
from app.ai.chat.orchestrator import get_chat_orchestrator
from app.ai.chat.sessions import ChatSessionStore
from app.auth.dependencies import get_current_user
from app.config import settings

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
    message_timestamps: deque[float] = deque()
    rate_limit_window = max(1, settings.CHAT_RATE_LIMIT_WINDOW_SECONDS)
    rate_limit_max = max(1, settings.CHAT_RATE_LIMIT_MAX_MESSAGES)

    try:
        await websocket.send_json(
            {
                "type": ChatEventType.INFO.value,
                "message": "Chat connection established",
                "session_id": session.session_id,
            }
        )

        summary, history = await session_store.hydrate_context(
            session=session,
            limit=settings.CHAT_RECENT_MESSAGE_LIMIT,
        )
        if summary:
            await websocket.send_json(
                {
                    "type": ChatEventType.SUMMARY.value,
                    "data": {"summary": summary},
                }
            )
        if history:
            await websocket.send_json(
                {
                    "type": ChatEventType.HISTORY.value,
                    "data": {"messages": history},
                }
            )

        while True:
            payload = await websocket.receive_json()
            message = payload.get("message")
            if not message:
                continue

            now = time.monotonic()
            while message_timestamps and now - message_timestamps[0] > rate_limit_window:
                message_timestamps.popleft()
            if len(message_timestamps) >= rate_limit_max:
                await websocket.send_json(
                    {
                        "type": ChatEventType.ERROR.value,
                        "data": {
                            "message": "Rate limit exceeded. Please slow down before sending another message.",
                        },
                    }
                )
                continue
            message_timestamps.append(now)

            async for event in orchestrator.stream_response(
                message=message,
                user_context=current_user,
                session=session,
            ):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        pass
