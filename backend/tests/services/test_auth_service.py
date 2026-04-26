import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from services.auth.service import (
    get_user_by_email,
    build_user_payload,
    build_auth_response,
    register_user,
    authenticate_user,
)


# ---------------------------
# get_user_by_email
# ---------------------------
@pytest.mark.asyncio
async def test_get_user_by_email_found(db: AsyncSession):
    user = User(full_name="Test", email="test@example.com", hashed_password="pass")
    db.add(user)
    await db.commit()

    result = await get_user_by_email(db, "test@example.com")

    assert result is not None
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(db: AsyncSession):
    result = await get_user_by_email(db, "missing@example.com")
    assert result is None


# ---------------------------
# build_user_payload
# ---------------------------
def test_build_user_payload():
    user = User(id="1", full_name="Test User", email="test@example.com", hashed_password="x")

    payload = build_user_payload(user)

    assert payload.id == "1"
    assert payload.full_name == "Test User"
    assert payload.email == "test@example.com"


# ---------------------------
# build_auth_response
# ---------------------------
def test_build_auth_response(monkeypatch):
    user = User(id="1", full_name="Test User", email="test@example.com", hashed_password="x")

    # Mock token generator
    monkeypatch.setattr(
        "services.auth.service.create_access_token",
        lambda data: "fake-token"
    )

    response = build_auth_response(user)

    assert response["token"] == "fake-token"
    assert response["user"]["email"] == "test@example.com"


# ---------------------------
# register_user
# ---------------------------
@pytest.mark.asyncio
async def test_register_user_success(db: AsyncSession, monkeypatch):
    # Mock password hashing
    monkeypatch.setattr(
        "services.auth.service.hash_password",
        lambda pwd: "hashed-password"
    )

    user = await register_user(
        db,
        full_name="Test",
        email="new@example.com",
        password="1234"
    )

    assert user.email == "new@example.com"
    assert user.hashed_password == "hashed-password"


@pytest.mark.asyncio
async def test_register_user_existing_email(db: AsyncSession):
    # Insert existing user
    user = User(full_name="Test", email="exists@example.com", hashed_password="pass")
    db.add(user)
    await db.commit()

    with pytest.raises(HTTPException) as exc:
        await register_user(db, "Test", "exists@example.com", "1234")

    assert exc.value.status_code == 400


# ---------------------------
# authenticate_user
# ---------------------------
@pytest.mark.asyncio
async def test_authenticate_user_success(db: AsyncSession, monkeypatch):
    user = User(full_name="Test", email="test@example.com", hashed_password="hashed")
    db.add(user)
    await db.commit()

    # Mock password verification
    monkeypatch.setattr(
        "services.auth.service.verify_password",
        lambda plain, hashed: True
    )

    result = await authenticate_user(db, "test@example.com", "1234")

    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(db: AsyncSession, monkeypatch):
    user = User(full_name="Test", email="test@example.com", hashed_password="hashed")
    db.add(user)
    await db.commit()

    monkeypatch.setattr(
        "services.auth.service.verify_password",
        lambda plain, hashed: False
    )

    with pytest.raises(HTTPException) as exc:
        await authenticate_user(db, "test@example.com", "wrong")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_authenticate_user_not_found(db: AsyncSession):
    with pytest.raises(HTTPException) as exc:
        await authenticate_user(db, "missing@example.com", "1234")

    assert exc.value.status_code == 401