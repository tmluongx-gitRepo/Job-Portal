"""
Authentication API routes for Supabase integration.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    CurrentUser,
    MessageResponse,
    PasswordReset,
    PasswordUpdate,
    TokenResponse,
    UserInfo,
    UserSignIn,
    UserSignUp,
)
from app.auth.supabase_client import supabase

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserSignUp):
    """
    Register a new user with email and password.
    
    Creates a new user in Supabase Auth and stores account type in user metadata.
    
    Args:
        user_data: User registration data including email, password, account_type
        
    Returns:
        TokenResponse: Access token, refresh token, and user information
        
    Raises:
        HTTPException: 400 if registration fails (e.g., email already exists)
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    try:
        # Sign up user with Supabase
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "account_type": user_data.account_type,
                    "full_name": user_data.full_name,
                }
            }
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed"
            )

        # Check if email confirmation is required (no session returned)
        if not response.session:
            return {
                "message": "Registration successful. Please check your email to confirm your account.",
                "user_id": response.user.id,
                "email": response.user.email,
                "email_confirmation_required": True
            }

        # Extract user info
        user_info = UserInfo(
            id=response.user.id,
            email=response.user.email,
            account_type=user_data.account_type,
            email_verified=response.user.email_confirmed_at is not None,
            provider="email",
            created_at=response.user.created_at,
        )

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in,
            user=user_info,
        )

    except Exception as e:
        # Handle Supabase auth errors
        error_message = str(e)
        if "already registered" in error_message.lower() or "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserSignIn):
    """
    Log in with email and password.
    
    Args:
        credentials: User email and password
        
    Returns:
        TokenResponse: Access token, refresh token, and user information
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    try:
        # Sign in with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })

        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Extract user metadata
        user_metadata = response.user.user_metadata or {}

        user_info = UserInfo(
            id=response.user.id,
            email=response.user.email,
            account_type=user_metadata.get("account_type"),
            email_verified=response.user.email_confirmed_at is not None,
            provider=response.user.app_metadata.get("provider", "email"),
            created_at=response.user.created_at,
        )

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in,
            user=user_info,
        )

    except Exception as e:
        error_message = str(e)
        if "invalid" in error_message.lower() or "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {error_message}"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Log out current user.
    
    Invalidates the current session in Supabase.
    
    Args:
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        MessageResponse: Success message
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    try:
        # Sign out from Supabase
        supabase.auth.sign_out()

        return MessageResponse(message="Successfully logged out")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {e!s}"
        )


@router.get("/me", response_model=CurrentUser)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        CurrentUser: Current user information
    """
    return CurrentUser(**current_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        TokenResponse: New access token and user information
        
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    try:
        # Refresh session with Supabase
        response = supabase.auth.refresh_session(refresh_token)

        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_metadata = response.user.user_metadata or {}

        user_info = UserInfo(
            id=response.user.id,
            email=response.user.email,
            account_type=user_metadata.get("account_type"),
            email_verified=response.user.email_confirmed_at is not None,
            provider=response.user.app_metadata.get("provider", "email"),
            created_at=response.user.created_at,
        )

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in,
            user=user_info,
        )

    except Exception as e:
        error_message = str(e)
        if "invalid" in error_message.lower() or "expired" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {error_message}"
        )


@router.post("/password-reset/request", response_model=MessageResponse)
async def request_password_reset(data: PasswordReset):
    """
    Request password reset email.
    
    Sends a password reset link to the user's email.
    
    Args:
        data: Email address
        
    Returns:
        MessageResponse: Success message (always returns success for security)
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    try:
        # Request password reset from Supabase
        supabase.auth.reset_password_email(data.email)

        # Always return success for security (don't reveal if email exists)
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )

    except Exception:
        # Still return success message for security
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )


@router.patch("/password", response_model=MessageResponse)
async def update_password(
    data: PasswordUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's password.
    
    Requires user to be authenticated.
    
    Args:
        data: New password
        current_user: Current authenticated user
        
    Returns:
        MessageResponse: Success message
        
    Raises:
        HTTPException: 400 if password update fails
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    try:
        # Update password in Supabase
        supabase.auth.update_user({"password": data.password})

        return MessageResponse(message="Password updated successfully")

    except Exception as e:
        error_message = str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password update failed: {error_message}"
        )

