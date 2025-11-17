"""Chat streaming endpoint scaffolding."""

from __future__ import annotations

import time
from collections import deque

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ai.chat.constants import ChatEventType
from app.ai.chat.orchestrator import get_chat_orchestrator
from app.ai.chat.sessions import ChatSessionStore
from app.auth import user_service
from app.auth.auth_utils import (
    ExpiredTokenError,
    InvalidTokenError,
    decode_supabase_jwt,
    extract_user_from_token,
)
from app.config import settings

router = APIRouter()


def _validate_user_payload(supabase_user: dict) -> None:
    """Validate user payload has required fields."""
    if not supabase_user.get("id") or not supabase_user.get("email"):
        raise InvalidTokenError("Invalid token payload")


@router.websocket("/api/chat/ws")
async def chat_websocket(websocket: WebSocket) -> None:
    """Authenticate the websocket and initialise a chat session.

    Real streaming logic will be added in subsequent phases. For now this echoes
    messages back through the orchestrator stub so we can exercise the plumbing.
    """
    token = websocket.query_params.get("access_token")
    if not token:
        await websocket.close(code=4001, reason="Missing access token")
        return

    try:
        payload = decode_supabase_jwt(token)
        supabase_user = extract_user_from_token(payload)
        _validate_user_payload(supabase_user)

        user_doc = await user_service.get_or_create_user_by_supabase_id(
            supabase_id=supabase_user["id"],
            email=supabase_user["email"],
            account_type=supabase_user.get("account_type", "job_seeker"),
        )
        current_user = {
            "id": str(user_doc["_id"]),
            "email": user_doc["email"],
            "account_type": user_doc.get("account_type", "job_seeker"),
            "provider": supabase_user.get("provider", "email"),
            "email_verified": supabase_user.get("email_verified", False),
            "role": supabase_user.get("role", "authenticated"),
            "metadata": supabase_user.get("metadata", {}),
        }
    except ExpiredTokenError:
        await websocket.close(code=4002, reason="Token expired")
        return
    except InvalidTokenError:
        await websocket.close(code=4003, reason="Invalid token")
        return
    except Exception:
        await websocket.close(code=1011, reason="Authentication failed")
        return

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
                "data": {
                    "message": "Chat connection established",
                    "session_id": session.session_id,
                },
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
