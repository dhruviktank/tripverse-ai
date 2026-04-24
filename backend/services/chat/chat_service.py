"""Chat service for conversational trip planning."""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

from llm.factory import get_llm_client
from orchestrator.graph import get_trip_planning_orchestrator
from schemas.chat import ConversationContext, Message
from services.chat.session_store import BaseSessionStore, InMemorySessionStore

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat conversations and context extraction."""

    # System prompt for conversational chat
    SYSTEM_PROMPT = """You are a helpful and friendly AI travel assistant for TripVerse, a trip planning platform.

Your responsibilities:
1. Have natural, engaging conversations about travel plans
2. Ask clarifying questions to understand the user's travel preferences
3. Extract and remember trip details (destination, duration, budget, preferences, etc.)
4. Provide travel recommendations and suggestions
5. Guide users toward trip planning when they have enough information
6. Be professional but conversational in tone

When users provide trip information, extract:
- Source/starting location
- Destination(s)
- Trip duration
- Budget level
- Travel pace preference
- Specific interests/preferences
- Trip description

If the user seems ready to generate a full trip plan (has provided at least a destination and duration), 
suggest generating a plan with the action: "generate_plan"

Keep responses concise (2-3 sentences typically) and friendly."""

    # Context extraction prompt
    CONTEXT_EXTRACTION_PROMPT = """Analyze the conversation history below and extract structured trip planning information.

Return a JSON object with this exact structure:
{{
  "source": "<starting location or null>",
  "destinations": ["<destination1>", "<destination2>", ...],
  "preferences": ["<preference1>", "<preference2>", ...],
  "budget": "<Budget level: 'Budget explorer', 'Balanced', 'Luxury' or null>",
  "pace": "<Travel pace: 'Relaxed', 'Balanced', 'High energy' or null>",
  "duration_days": <number or null>,
  "trip_description": "<brief description or null>"
}}

Conversation:
{conversation}

Only include information that was explicitly mentioned or clearly implied. Use null for unknown values.
Return ONLY the JSON object, no other text."""

    def __init__(self, session_store: Optional[BaseSessionStore] = None):
        """Initialize chat service.

        Args:
            session_store: Session store backend (defaults to in-memory)
        """
        self.session_store = session_store or InMemorySessionStore()
        self.llm_client = get_llm_client()
        self.orchestrator = get_trip_planning_orchestrator()
        self.max_context_messages = 10

    async def handle_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Handle a user message and generate a response.

        Args:
            session_id: Session identifier
            user_message: User message text

        Returns:
            Dictionary with reply, context, and metadata
        """
        try:
            # Validate input
            if not session_id or not user_message:
                return {
                    "reply": "I need both a session ID and message to help you.",
                    "session_id": session_id,
                    "context": None,
                    "requires_clarification": True,
                    "suggested_action": None,
                }

            # Ensure session exists
            if not await self.session_store.session_exists(session_id):
                await self.session_store.create_session(session_id)

            # Add user message to session
            await self.session_store.add_message(session_id, "user", user_message)

            # Get recent messages for context
            recent_messages = await self.session_store.get_messages(session_id, self.max_context_messages)

            # Generate response
            reply = await self._generate_response(recent_messages)

            # Add assistant message to session
            await self.session_store.add_message(session_id, "assistant", reply)

            # Extract context from conversation
            context = await self._extract_context(recent_messages + [Message(role="assistant", content=reply)])

            # Update session context
            await self.session_store.update_context(session_id, context)

            # Determine if user is ready to generate plan
            suggested_action = self._suggest_action(context, reply)

            return {
                "reply": reply,
                "session_id": session_id,
                "context": context.model_dump() if context else None,
                "requires_clarification": self._check_clarification_needed(context),
                "suggested_action": suggested_action,
            }

        except Exception as exc:
            logger.error(f"Error handling message in session {session_id}: {exc}")
            return {
                "reply": f"I encountered an error processing your message: {str(exc)}",
                "session_id": session_id,
                "context": None,
                "requires_clarification": True,
                "suggested_action": None,
            }

    async def handle_message_stream(self, session_id: str, user_message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle a user message with streaming response.

        Args:
            session_id: Session identifier
            user_message: User message text

        Yields:
            Event dictionaries for streaming
        """
        try:
            # Validate input
            if not session_id or not user_message:
                yield {
                    "event_type": "error",
                    "session_id": session_id,
                    "data": "Invalid session ID or message",
                    "context": None,
                }
                return

            # Ensure session exists
            if not await self.session_store.session_exists(session_id):
                await self.session_store.create_session(session_id)

            # Add user message
            await self.session_store.add_message(session_id, "user", user_message)

            # Yield start event
            yield {"event_type": "start", "session_id": session_id, "data": None, "context": None}

            # Get recent messages
            recent_messages = await self.session_store.get_messages(session_id, self.max_context_messages)

            # Stream response
            full_response = ""
            async for chunk in self._stream_response(recent_messages):
                full_response += chunk
                yield {
                    "event_type": "chunk",
                    "session_id": session_id,
                    "data": chunk,
                    "context": None,
                }

            # Add assistant message
            await self.session_store.add_message(session_id, "assistant", full_response)

            # Extract context
            context = await self._extract_context(
                recent_messages + [Message(role="assistant", content=full_response)]
            )
            await self.session_store.update_context(session_id, context)

            # Suggest action
            suggested_action = self._suggest_action(context, full_response)

            # Yield end event with final context
            yield {
                "event_type": "end",
                "session_id": session_id,
                "data": None,
                "context": context.model_dump() if context else None,
                "suggested_action": suggested_action,
            }

        except Exception as exc:
            logger.error(f"Error streaming message in session {session_id}: {exc}")
            yield {
                "event_type": "error",
                "session_id": session_id,
                "data": f"Error: {str(exc)}",
                "context": None,
            }

    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information.

        Args:
            session_id: Session identifier

        Returns:
            Session info or None if not found
        """
        if not await self.session_store.session_exists(session_id):
            return None

        messages = await self.session_store.get_messages(session_id, limit=100)
        context = await self.session_store.get_context(session_id)

        return {
            "session_id": session_id,
            "message_count": len(messages),
            "context": context.model_dump() if context else None,
            "messages": [msg.model_dump() for msg in messages[-5:]],  # Last 5 for preview
        }

    async def clear_session(self, session_id: str) -> bool:
        """Clear a session.

        Args:
            session_id: Session identifier

        Returns:
            True if cleared, False if not found
        """
        result = await self.session_store.delete_session(session_id)
        if result:
            logger.info(f"Session cleared: {session_id}")
        return result

    # ==================== Private Methods ====================

    async def _generate_response(self, recent_messages: list[Message]) -> str:
        """Generate conversational response using LLM.

        Args:
            recent_messages: Recent message history

        Returns:
            Generated response text
        """
        # Build conversation context
        conversation = "\n".join(
            [f"{msg.role.upper()}: {msg.content}" for msg in recent_messages]
        )

        try:
            response = await self.llm_client.generate(
                prompt=conversation,
                system_prompt=self.SYSTEM_PROMPT,
            )
            return response.strip()
        except Exception as exc:
            logger.error(f"LLM generation error: {exc}")
            return "I'm experiencing technical difficulties. Could you please try again?"

    async def _stream_response(self, recent_messages: list[Message]) -> AsyncGenerator[str, None]:
        """Stream conversational response using LLM.

        Args:
            recent_messages: Recent message history

        Yields:
            Response chunks
        """
        conversation = "\n".join(
            [f"{msg.role.upper()}: {msg.content}" for msg in recent_messages]
        )

        try:
            async for chunk in self.llm_client.stream_generate(
                prompt=conversation,
                system_prompt=self.SYSTEM_PROMPT,
            ):
                yield chunk
        except Exception as exc:
            logger.error(f"LLM streaming error: {exc}")
            yield "I'm experiencing technical difficulties. Could you please try again?"

    async def _extract_context(self, messages: list[Message]) -> Optional[ConversationContext]:
        """Extract structured context from conversation.

        Args:
            messages: Message history

        Returns:
            Extracted context or None
        """
        try:
            # Build conversation for extraction
            conversation = "\n".join(
                [f"{msg.role.upper()}: {msg.content}" for msg in messages]
            )

            prompt = self.CONTEXT_EXTRACTION_PROMPT.format(conversation=conversation)

            # Get structured response
            response = await self.llm_client.generate(prompt=prompt)

            # Parse JSON
            json_str = response.strip()
            # Handle potential markdown code blocks
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                json_str = json_str.strip()

            context_data = json.loads(json_str)

            return ConversationContext(**context_data)

        except Exception as exc:
            logger.error(f"Context extraction error: {exc}")
            return ConversationContext()

    def _check_clarification_needed(self, context: Optional[ConversationContext]) -> bool:
        """Check if more clarification is needed.

        Args:
            context: Extracted context

        Returns:
            True if clarification needed
        """
        if not context:
            return True

        # Need at least destination and duration
        has_destination = context.destinations and len(context.destinations) > 0
        has_duration = context.duration_days is not None and context.duration_days > 0

        return not (has_destination and has_duration)

    def _suggest_action(self, context: Optional[ConversationContext], reply: str) -> Optional[str]:
        """Suggest next action based on context.

        Args:
            context: Extracted context
            reply: Assistant reply

        Returns:
            Suggested action or None
        """
        if not context:
            return None

        # Check if we have enough info for planning
        has_destination = context.destinations and len(context.destinations) > 0
        has_duration = context.duration_days is not None and context.duration_days > 0

        # Show generate plan button when user has provided destination and duration
        if has_destination and has_duration:
            return "generate_plan"

        return None

    async def generate_plan_from_context(self, session_id: str) -> Dict[str, Any]:
        """Generate trip plan from extracted context.

        Args:
            session_id: Session identifier

        Returns:
            Plan result
        """
        try:
            context = await self.session_store.get_context(session_id)
            if not context:
                return {"success": False, "error": "No context found for session"}

            # Validate minimum required fields
            if not context.destinations or len(context.destinations) == 0:
                return {
                    "success": False,
                    "error": "Please tell me where you'd like to go. I need at least one destination to plan your trip.",
                    "requires_destination": True,
                }

            if not context.duration_days or context.duration_days <= 0:
                return {
                    "success": False,
                    "error": "How many days would you like to travel? I need the trip duration to create your itinerary.",
                    "requires_duration": True,
                }

            # Build trip input from context with sensible defaults
            destinations_list = []
            for idx, dest in enumerate(context.destinations):
                if dest:  # Filter out empty strings
                    destinations_list.append({"name": dest.strip(), "confidence": 0.95 - (idx * 0.05)})

            if not destinations_list:
                return {
                    "success": False,
                    "error": "I couldn't find valid destinations in our conversation. Please mention where you'd like to visit.",
                    "requires_destination": True,
                }

            trip_input = {
                "trip_description": context.trip_description or f"Trip to {', '.join(context.destinations)}",
                "duration_days": max(1, min(30, context.duration_days)),  # Clamp between 1-30 days
                "preferences": [p.strip() for p in (context.preferences or []) if p],  # Filter empty
                "source": {"name": context.source.strip(), "confidence": 1.0} if context.source and context.source.strip() else None,
                "destinations": destinations_list,
                "budget": context.budget or "Balanced",
                "pace": context.pace or "Balanced",
                "confirm_intent": True,
            }

            # Use orchestrator to generate plan
            result = await self.orchestrator.plan_trip(trip_input)

            return result

        except Exception as exc:
            logger.error(f"Error generating plan from session {session_id}: {exc}")
            return {
                "success": False,
                "error": f"I encountered an error generating your plan: {str(exc)}. Please try asking me a few more questions about your trip preferences and we can try again.",
            }


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create chat service singleton.

    Returns:
        ChatService instance
    """
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
