"""
User API routes.
"""

from fastapi import APIRouter, HTTPException, status

from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user."""
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
async def get_users(skip: int = 0, limit: int = 100):
    """Get all users."""
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


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID."""
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
async def get_user_by_email(email: str):
    """Get user by email."""
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


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user."""
    # Build update dict (only include provided fields)
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Delete user."""
    deleted = await user_crud.delete_user(user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
