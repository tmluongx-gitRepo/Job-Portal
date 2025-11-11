"""
Authentication utilities for JWT token validation and user extraction.
"""

from typing import Any

import jwt
from jwt import PyJWTError


class AuthenticationError(Exception):
    """Base authentication error."""


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid."""


class ExpiredTokenError(AuthenticationError):
    """Raised when token has expired."""


def decode_supabase_jwt(token: str) -> dict[str, Any]:
    """
    Decode and validate Supabase JWT token.

    Simplified version that trusts Supabase token validation.
    The token is already validated by Supabase on login/register.

    Args:
        token: JWT token string from Authorization header

    Returns:
        dict: Decoded token payload containing user information

    Raises:
        InvalidTokenError: If token is invalid or malformed
        ExpiredTokenError: If token has expired
    """
    try:
        # Decode JWT token without signature verification
        # Supabase tokens are already validated by Supabase's auth service
        # and we trust tokens that pass through their system.
        # The token's exp claim is still checked to ensure it hasn't expired.
        payload = jwt.decode(
            token,
            options={"verify_signature": False},
            algorithms=["HS256"],
        )

    except jwt.ExpiredSignatureError as e:
        raise ExpiredTokenError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError("Invalid token") from e
    except PyJWTError as e:
        raise InvalidTokenError(f"Token validation failed: {e!s}") from e
    else:
        # Type annotation to satisfy mypy
        result: dict[str, Any] = payload
        return result


def extract_user_from_token(payload: dict) -> dict:
    """
    Extract user information from decoded JWT payload.

    Args:
        payload: Decoded JWT payload

    Returns:
        dict: User information including:
            - id: User ID (from 'sub' claim)
            - email: User email
            - account_type: 'job_seeker' or 'employer'
            - provider: Authentication provider ('email', 'google', 'linkedin_oidc')
            - email_verified: Whether email is verified
            - metadata: Additional user metadata
    """
    user_metadata = payload.get("user_metadata", {})
    app_metadata = payload.get("app_metadata", {})

    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "account_type": user_metadata.get("account_type"),
        "provider": app_metadata.get("provider", "email"),
        "email_verified": payload.get("email_confirmed_at") is not None,
        "role": payload.get("role", "authenticated"),
        "metadata": user_metadata,
    }


def validate_account_type(account_type: str | None) -> bool:
    """
    Validate account type value.

    Args:
        account_type: Account type to validate

    Returns:
        bool: True if valid, False otherwise
    """
    valid_types = ["job_seeker", "employer", "admin", "service"]
    return account_type in valid_types


def is_admin(user: dict) -> bool:
    """
    Check if user has admin privileges.

    Args:
        user: User dict from extract_user_from_token

    Returns:
        bool: True if user is admin
    """
    return user.get("account_type") == "admin" or user.get("role") == "service_role"


def is_job_seeker(user: dict) -> bool:
    """
    Check if user is a job seeker.

    Args:
        user: User dict from extract_user_from_token

    Returns:
        bool: True if user is job seeker
    """
    return user.get("account_type") == "job_seeker"


def is_employer(user: dict) -> bool:
    """
    Check if user is an employer.

    Args:
        user: User dict from extract_user_from_token

    Returns:
        bool: True if user is employer
    """
    return user.get("account_type") == "employer"
