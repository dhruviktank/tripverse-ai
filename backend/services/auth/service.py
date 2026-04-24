"""Authentication business logic and persistence helpers."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import create_access_token, hash_password, verify_password
from models import User


@dataclass(frozen=True)
class AuthUserPayload:
    """Minimal user payload returned by auth operations."""

    id: str
    full_name: str
    email: str


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Return a user by email if it exists."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def build_user_payload(user: User) -> AuthUserPayload:
    """Convert a user model into a response payload."""
    return AuthUserPayload(id=user.id, full_name=user.full_name, email=user.email)


def build_auth_response(user: User) -> dict:
    """Create a token and response payload for the given user."""
    payload = build_user_payload(user)
    token = create_access_token({"sub": user.id, "email": user.email})
    return {
        "token": token,
        "user": {"id": payload.id, "full_name": payload.full_name, "email": payload.email},
    }


async def register_user(db: AsyncSession, full_name: str, email: str, password: str) -> User:
    """Register a new user or raise a conflict if the email already exists."""
    existing_user = await get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An account with this email already exists")

    user = User(full_name=full_name, email=email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """Validate credentials and return the authenticated user."""
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return user
