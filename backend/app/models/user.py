"""
User model for ChromaDB.

In ChromaDB, users are stored as documents with metadata.
Each user document contains their profile information as metadata.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4


class User:
    """User model for ChromaDB."""

    def __init__(
        self,
        email: str,
        username: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
        user_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = user_id or str(uuid4())
        self.email = email
        self.username = username
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert user to dictionary for ChromaDB storage."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary."""
        return cls(
            user_id=data.get("id"),
            email=data["email"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            full_name=data.get("full_name"),
            is_active=data.get("is_active", True),
            is_superuser=data.get("is_superuser", False),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
        )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
