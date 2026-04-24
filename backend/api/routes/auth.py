"""Authentication API routes."""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_db
from models import User
from schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from services.auth.service import authenticate_user, build_auth_response, register_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, request.full_name, request.email, request.password)
    auth_data = build_auth_response(user)
    logger.info(f"New user registered: {user.email}")
    return AuthResponse(success=True, token=auth_data["token"], user=auth_data["user"], message="Account created successfully")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, request.email, request.password)
    auth_data = build_auth_response(user)
    logger.info(f"User logged in: {user.email}")
    return AuthResponse(success=True, token=auth_data["token"], user=auth_data["user"], message="Login successful")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        created_at=current_user.created_at.isoformat(),
    )
