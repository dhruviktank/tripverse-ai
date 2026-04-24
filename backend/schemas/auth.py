"""Authentication API schemas."""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class AuthResponse(BaseModel):
    success: bool
    token: str | None = None
    user: dict | None = None
    message: str | None = None


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    created_at: str
