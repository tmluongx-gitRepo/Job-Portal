"""
FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth import user_service
from app.auth.auth_utils import (
    ExpiredTokenError,
    InvalidTokenError,
    decode_supabase_jwt,
    extract_user_from_token,
    is_admin,
    is_employer,
    is_job_seeker,
)


def _raise_invalid_token_payload() -> None:
    """Raise HTTPException for invalid token payload."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token payload",
        headers={"WWW-Authenticate": "Bearer"},
    )


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token.

    Extracts JWT token from Authorization header, validates it,
    and returns user information. Auto-creates MongoDB user record
    on first authentication (Just-In-Time provisioning).

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        dict: User information including id, email, account_type, etc.

    Raises:
        HTTPException: 401 if token is invalid or expired

    Usage:
        @router.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            return {"user_id": current_user["id"]}
    """
    token = credentials.credentials

    try:
        # Decode and validate JWT token
        payload = decode_supabase_jwt(token)

        # Extract user information
        user = extract_user_from_token(payload)

        # Ensure user has required fields
        if not user.get("id") or not user.get("email"):
            _raise_invalid_token_payload()

        # Just-In-Time (JIT) user provisioning via service layer
        # Converts Supabase UUID to MongoDB ObjectId
        user_doc = await user_service.get_or_create_user_by_supabase_id(
            supabase_id=user["id"],
            email=user["email"],
            account_type=user.get("account_type", "job_seeker"),
        )

        # Return user info with MongoDB ObjectId as primary ID
        # Include all fields required by CurrentUser schema
        return {
            "id": str(user_doc["_id"]),  # MongoDB ObjectId (primary ID)
            "email": user_doc["email"],
            "account_type": user_doc["account_type"],
            "provider": user.get("provider", "email"),
            "email_verified": user.get("email_verified", False),
            "role": user.get("role", "authenticated"),
            "metadata": user.get("metadata", {}),
        }

    except ExpiredTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> dict | None:
    """
    Dependency to get current user if authenticated, None otherwise.

    Useful for endpoints that work for both authenticated and anonymous users.
    Returns MongoDB user document with _id (not Supabase UUID).

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        dict | None: User information with MongoDB _id if authenticated, None otherwise

    Usage:
        @router.get("/jobs")
        async def list_jobs(current_user: Optional[dict] = Depends(get_optional_user)):
            # Show different data based on authentication
            if current_user:
                return {"jobs": jobs, "recommended": True}
            return {"jobs": public_jobs}
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = decode_supabase_jwt(token)
        supabase_user = extract_user_from_token(payload)

        # Just-in-time user provisioning - get or create MongoDB user
        from app.auth.user_service import get_or_create_user_by_supabase_id

        account_type = supabase_user.get("account_type") or "job_seeker"
        user_doc = await get_or_create_user_by_supabase_id(
            supabase_id=supabase_user["id"],
            email=supabase_user["email"],
            account_type=account_type,
        )

        # Return MongoDB user with ObjectId as 'id'
        # Include all fields for consistency with get_current_user
        return {
            "id": user_doc["_id"],
            "email": user_doc["email"],
            "account_type": user_doc["account_type"],
            "provider": supabase_user.get("provider", "email"),
            "email_verified": supabase_user.get("email_verified", False),
            "role": supabase_user.get("role", "authenticated"),
            "metadata": supabase_user.get("metadata", {}),
        }
    except (InvalidTokenError, ExpiredTokenError):
        return None


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin privileges.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: User information

    Raises:
        HTTPException: 403 if user is not admin

    Usage:
        @router.delete("/users/{user_id}")
        async def delete_user(
            user_id: str,
            admin: dict = Depends(require_admin)
        ):
            # Only admins can delete users
            pass
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user


async def require_job_seeker(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require job seeker account.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: User information

    Raises:
        HTTPException: 403 if user is not a job seeker

    Usage:
        @router.post("/applications")
        async def apply_to_job(
            job_id: str,
            job_seeker: dict = Depends(require_job_seeker)
        ):
            # Only job seekers can apply
            pass
    """
    if not is_job_seeker(current_user) and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Job seeker account required"
        )
    return current_user


async def require_employer(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require employer account.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: User information

    Raises:
        HTTPException: 403 if user is not an employer

    Usage:
        @router.post("/jobs")
        async def create_job(
            job_data: JobCreate,
            employer: dict = Depends(require_employer)
        ):
            # Only employers can post jobs
            pass
    """
    if not is_employer(current_user) and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Employer account required"
        )
    return current_user


async def require_job_seeker_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require job seeker or admin account.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: User information

    Raises:
        HTTPException: 403 if user is neither job seeker nor admin
    """
    if not is_job_seeker(current_user) and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Job seeker account or admin privileges required",
        )
    return current_user


async def require_employer_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require employer or admin account.

    Args:
        current_user: Current authenticated user

    Returns:
        dict: User information

    Raises:
        HTTPException: 403 if user is neither employer nor admin
    """
    if not is_employer(current_user) and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employer account or admin privileges required",
        )
    return current_user
