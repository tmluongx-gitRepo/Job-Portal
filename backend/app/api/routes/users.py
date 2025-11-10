"""
User API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user, require_admin
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, _admin: dict = Depends(require_admin)) -> UserResponse:
    """
    Create a new user.

    **Requires:** Admin account
    **Note:** Regular users should use `/api/auth/register` instead

    This endpoint is for admin user management only.
    """
    try:
        created_user = await user_crud.create_user(email=user.email, account_type=user.account_type)

        # Convert ObjectId to string for response
        return UserResponse(
            id=str(created_user["_id"]),
            email=created_user["email"],
            account_type=created_user["account_type"],
            created_at=created_user["created_at"],
            updated_at=created_user["updated_at"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[UserResponse])
async def get_users(
    _admin: dict = Depends(require_admin), skip: int = 0, limit: int = 100
) -> list[UserResponse]:
    """
    Get all users.

    **Requires:** Admin account

    For user management and system administration.
    """
    users = await user_crud.get_users(skip=skip, limit=limit)

    return [
        UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            account_type=user["account_type"],
            created_at=user["created_at"],
            updated_at=user["updated_at"],
        )
        for user in users
    ]


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """
    Get your own user information.

    **Requires:** Authentication

    Convenient endpoint to get your own account details.
    """
    user = await user_crud.get_user_by_id(current_user["id"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        account_type=user["account_type"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)) -> UserResponse:
    """
    Get user by ID.

    **Requires:** Authentication
    **Authorization:** Owner or Admin

    You can view your own account or admins can view any account.
    """
    # Check if viewing own account or is admin
    from app.auth.utils import is_admin

    if user_id != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own account"
        )

    user = await user_crud.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        account_type=user["account_type"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, _admin: dict = Depends(require_admin)) -> UserResponse:
    """
    Get user by email.

    **Requires:** Admin account

    For user lookup and administration.
    """
    user = await user_crud.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        account_type=user["account_type"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate, current_user: dict = Depends(get_current_user)
) -> UserResponse:
    """
    Update your own user information.

    **Requires:** Authentication
    **Note:** You cannot change your account_type - contact an admin for that.
    """
    # Build update dict (only include provided fields)
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Users cannot change their own account_type
    if "account_type" in update_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your account type. Contact an administrator.",
        )

    updated_user = await user_crud.update_user(current_user["id"], update_data)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        account_type=updated_user["account_type"],
        created_at=updated_user["created_at"],
        updated_at=updated_user["updated_at"],
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, user_update: UserUpdate, current_user: dict = Depends(get_current_user)
) -> UserResponse:
    """
    Update user by ID.

    **Requires:** Authentication
    **Authorization:** Owner or Admin

    - Regular users can only update their own account (and cannot change account_type)
    - Admins can update any account including account_type
    """
    # Check if updating own account or is admin
    from app.auth.utils import is_admin

    is_own_account = user_id == current_user["id"]
    is_admin_user = is_admin(current_user)

    if not is_own_account and not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own account"
        )

    # Build update dict (only include provided fields)
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Non-admins cannot change account_type
    if "account_type" in update_data and not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can change account type"
        )

    updated_user = await user_crud.update_user(user_id, update_data)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        account_type=updated_user["account_type"],
        created_at=updated_user["created_at"],
        updated_at=updated_user["updated_at"],
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(current_user: dict = Depends(get_current_user)) -> None:
    """
    Delete your own account.

    **Requires:** Authentication

    Permanently deletes your account and all associated data.
    This action cannot be undone.
    """
    deleted = await user_crud.delete_user(current_user["id"])

    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)) -> None:
    """
    Delete user by ID.

    **Requires:** Authentication
    **Authorization:** Owner or Admin

    - You can delete your own account
    - Admins can delete any account

    Permanently deletes the account and all associated data.
    This action cannot be undone.
    """
    # Check if deleting own account or is admin
    from app.auth.utils import is_admin

    if user_id != current_user["id"] and not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own account"
        )

    deleted = await user_crud.delete_user(user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
