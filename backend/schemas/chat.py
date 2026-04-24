"""Chat API schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Individual message in conversation."""

    role: str = Field(..., description="Message sender: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")


class ConversationContext(BaseModel):
    """Extracted context from conversation."""

    source: Optional[str] = None
    destinations: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    budget: Optional[str] = None
    pace: Optional[str] = None
    duration_days: Optional[int] = None
    trip_description: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User message text")
    user_id: Optional[str] = Field(None, description="Optional user ID for persistence")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    reply: str = Field(..., description="Assistant's response message")
    session_id: str = Field(..., description="Session identifier")
    context: Optional[ConversationContext] = Field(None, description="Extracted trip context")
    requires_clarification: bool = Field(False, description="Whether clarification is needed")
    suggested_action: Optional[str] = Field(None, description="Suggested next action (e.g., 'generate_plan')")


class ChatStreamEvent(BaseModel):
    """Event model for streaming chat responses."""

    event_type: str = Field(..., description="Type of event: 'start', 'chunk', 'end', 'error'")
    session_id: str = Field(..., description="Session identifier")
    data: Optional[str] = Field(None, description="Event data (message chunk or error)")
    context: Optional[ConversationContext] = Field(None, description="Context at event time")


class SessionInfo(BaseModel):
    """Session information."""

    session_id: str = Field(..., description="Session identifier")
    message_count: int = Field(..., description="Number of messages in session")
    context: ConversationContext = Field(..., description="Current extracted context")
    last_message_at: Optional[str] = Field(None, description="ISO timestamp of last message")


class ClearSessionRequest(BaseModel):
    """Request to clear a session."""

    session_id: str = Field(..., description="Session identifier to clear")


class SessionResponse(BaseModel):
    """Response after session operation."""

    success: bool = Field(..., description="Whether operation succeeded")
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Operation result message")
