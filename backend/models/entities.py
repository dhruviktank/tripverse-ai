"""Database models for TripVerse AI."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class User(Base):
    """User table matching the frontend register form fields."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Trip(Base):
    """Trip table storing user trips with structured itinerary data."""

    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    trip_description: Mapped[str] = mapped_column(Text, nullable=False)
    budget: Mapped[str] = mapped_column(String(50), nullable=False)
    pace: Mapped[str] = mapped_column(String(50), nullable=False)
    starting_from: Mapped[str] = mapped_column(String(255), nullable=False)
    preferences: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="upcoming")
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    itinerary_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    itinerary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    budget_spent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_total: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    travelers: Mapped[int] = mapped_column(Integer, default=1)
    dates: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="trips")

    def __repr__(self) -> str:
        return f"<Trip {self.title}>"

    def to_dict(self) -> dict:
        """Convert trip to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "trip_description": self.trip_description,
            "budget": self.budget,
            "pace": self.pace,
            "starting_from": self.starting_from,
            "preferences": self.preferences,
            "status": self.status,
            "is_favorite": self.is_favorite,
            "itinerary_data": self.itinerary_data,
            "itinerary_text": self.itinerary_text,
            "budget_spent": self.budget_spent,
            "budget_total": self.budget_total,
            "travelers": self.travelers,
            "dates": self.dates,
            "thumbnail_url": self.thumbnail_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
