"""
Unit tests for JWT signature verification.

Tests the security-critical JWT decoding functionality to ensure:
- Valid tokens are accepted
- Forged tokens are rejected
- Expired tokens are rejected
- Tokens with wrong audience are rejected
"""

import time
from typing import Any

import jwt
import pytest

from app.auth.auth_utils import (
    ExpiredTokenError,
    InvalidTokenError,
    decode_supabase_jwt,
)
from app.config import settings


class TestJWTVerification:
    """Test JWT signature verification security."""

    def test_valid_token_is_accepted(self) -> None:
        """Valid tokens with correct signature should be accepted."""
        # Create a valid token
        payload = {
            "sub": "test-user-id",
            "email": "test@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "exp": int(time.time()) + 3600,  # Expires in 1 hour
            "iat": int(time.time()),
        }

        token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

        # Should decode successfully
        decoded = decode_supabase_jwt(token)
        assert decoded["sub"] == "test-user-id"
        assert decoded["email"] == "test@example.com"
        assert decoded["role"] == "authenticated"

    def test_forged_token_is_rejected(self) -> None:
        """Tokens with invalid signatures should be rejected."""
        # Create a token with wrong signature
        payload = {
            "sub": "hacker-user-id",
            "email": "hacker@example.com",
            "role": "admin",  # Trying to escalate privileges
            "aud": "authenticated",
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
        }

        # Sign with wrong secret
        wrong_secret = "wrong-secret-key"
        forged_token = jwt.encode(payload, wrong_secret, algorithm="HS256")

        # Should raise InvalidTokenError
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            decode_supabase_jwt(forged_token)

    def test_expired_token_is_rejected(self) -> None:
        """Expired tokens should be rejected."""
        # Create an expired token
        payload = {
            "sub": "test-user-id",
            "email": "test@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "exp": int(time.time()) - 3600,  # Expired 1 hour ago
            "iat": int(time.time()) - 7200,
        }

        token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

        # Should raise ExpiredTokenError
        with pytest.raises(ExpiredTokenError, match="Token has expired"):
            decode_supabase_jwt(token)

    def test_wrong_audience_is_rejected(self) -> None:
        """Tokens with wrong audience should be rejected."""
        # Create a token with wrong audience
        payload = {
            "sub": "test-user-id",
            "email": "test@example.com",
            "role": "authenticated",
            "aud": "wrong-audience",  # Wrong audience
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
        }

        token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

        # Should raise InvalidTokenError
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            decode_supabase_jwt(token)

    def test_malformed_token_is_rejected(self) -> None:
        """Malformed tokens should be rejected."""
        malformed_tokens = [
            "not.a.token",
            "only-one-part",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",
        ]

        for token in malformed_tokens:
            with pytest.raises(InvalidTokenError):
                decode_supabase_jwt(token)

    def test_token_without_required_claims(self) -> None:
        """Tokens missing required claims should be rejected."""
        # Token without 'aud' claim (audience is required)
        payload: dict[str, Any] = {
            "sub": "test-user-id",
            "email": "test@example.com",
            "exp": int(time.time()) + 3600,
            # Missing 'aud' - required by our verification
        }

        token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

        # Should raise InvalidTokenError due to missing audience
        with pytest.raises(InvalidTokenError):
            decode_supabase_jwt(token)

    def test_privilege_escalation_attempt(self) -> None:
        """Test that privilege escalation via forged tokens is prevented."""
        # Attacker tries to create admin token
        admin_payload = {
            "sub": "attacker-id",
            "email": "attacker@evil.com",
            "role": "admin",  # Trying to become admin
            "aud": "authenticated",
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "user_metadata": {"account_type": "admin"},
        }

        # Sign with wrong secret (attacker doesn't know real secret)
        fake_token = jwt.encode(admin_payload, "attacker-secret", algorithm="HS256")

        # Should be rejected
        with pytest.raises(InvalidTokenError):
            decode_supabase_jwt(fake_token)

    def test_jwt_secret_is_configured(self) -> None:
        """Ensure JWT secret is configured (critical for security)."""
        min_secret_length = 32  # Minimum length for strong JWT secrets
        assert settings.SUPABASE_JWT_SECRET, "SUPABASE_JWT_SECRET must be configured"
        assert len(settings.SUPABASE_JWT_SECRET) > min_secret_length, "JWT secret should be strong"

    def test_signature_verification_is_enabled(self) -> None:
        """Verify that signature verification is actually enabled in code."""
        import inspect

        source = inspect.getsource(decode_supabase_jwt)

        # Check that signature verification is enabled
        assert "verify_signature" in source, "Signature verification code not found"
        assert (
            '"verify_signature": True' in source or "'verify_signature': True" in source
        ), "Signature verification is not enabled"

        # Check that JWT secret is used
        assert "SUPABASE_JWT_SECRET" in source, "JWT secret is not used for verification"

        # Check that audience is validated
        assert (
            'audience="authenticated"' in source or "audience='authenticated'" in source
        ), "Audience validation not found"
