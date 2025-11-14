"""Chat agent constants and enums."""

from enum import Enum


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatEventType(str, Enum):
    INFO = "info"
    TOKEN = "token"
    COMPLETE = "complete"
    ERROR = "error"
