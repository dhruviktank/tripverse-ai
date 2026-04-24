"""Chat API routes."""

import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from schemas.chat import ChatRequest, ChatResponse, ChatStreamEvent, ClearSessionRequest, SessionResponse
from services.chat import get_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])
chat_service = get_chat_service()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Handle a chat message and return response.

    This endpoint accepts user messages, maintains conversation context,
    and returns AI-generated responses with extracted trip information.

    Args:
        request: Chat request with session_id and message

    Returns:
        Chat response with reply and extracted context

    Raises:
        HTTPException: If message handling fails
    """
    try:
        logger.info(f"Chat message received - Session: {request.session_id}")

        result = await chat_service.handle_message(request.session_id, request.message)

        return ChatResponse(
            reply=result["reply"],
            session_id=result["session_id"],
            context=result.get("context"),
            requires_clarification=result.get("requires_clarification", False),
            suggested_action=result.get("suggested_action"),
        )

    except Exception as exc:
        logger.error(f"Error in chat endpoint: {exc}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(exc)}")


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response in real-time.

    This endpoint streams the chat response using Server-Sent Events (SSE),
    allowing for real-time UI updates while the response is being generated.

    Args:
        request: Chat request with session_id and message

    Returns:
        StreamingResponse with NDJSON (newline-delimited JSON) events
    """

    async def event_generator():
        """Generate streaming events."""
        async for event in chat_service.handle_message_stream(request.session_id, request.message):
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")


@router.get("/session/{session_id}", status_code=status.HTTP_200_OK)
async def get_session_info(session_id: str):
    """Get session information.

    Returns details about a specific chat session including message count,
    extracted context, and recent messages.

    Args:
        session_id: Unique session identifier

    Returns:
        Session information or 404 if not found

    Raises:
        HTTPException: If session not found
    """
    try:
        session_info = await chat_service.get_session_info(session_id)


        if not session_info:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return session_info

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving session {session_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(exc)}")


@router.delete("/session/{session_id}", response_model=SessionResponse)
async def clear_session(session_id: str) -> SessionResponse:
    """Clear a chat session.

    Removes all conversation history and context for the specified session.

    Args:
        session_id: Unique session identifier

    Returns:
        Session response indicating success or failure

    Raises:
        HTTPException: If session not found
    """
    try:
        success = await chat_service.clear_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        return SessionResponse(
            success=True,
            session_id=session_id,
            message="Session cleared successfully",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error clearing session {session_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(exc)}")


@router.post("/plan/{session_id}")
async def generate_plan_from_chat(session_id: str):
    """Generate trip plan from chat context.

    Uses the extracted context from a chat session to generate a full trip plan
    using the existing orchestrator.

    Args:
        session_id: Unique session identifier

    Returns:
        Generated trip plan

    Raises:
        HTTPException: If session not found or plan generation fails
    """
    try:
        # Check session exists
        session_info = await chat_service.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Generate plan from context
        result = await chat_service.generate_plan_from_context(session_id)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to generate plan"))

        logger.info(f"Plan generated from chat session: {session_id}")

        return {"success": True, "plan": result.get("plan"), "session_id": session_id}

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error generating plan from session {session_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(exc)}")


@router.get("/health", status_code=status.HTTP_200_OK)
async def chat_health():
    """Health check for chat service.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": "chat"}
