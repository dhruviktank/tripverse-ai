"""Session store abstraction for chat conversations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from schemas.chat import ConversationContext, Message


class BaseSessionStore(ABC):
    """Abstract base class for session storage backends."""

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data."""
        raise NotImplementedError

    @abstractmethod
    async def create_session(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new session."""
        raise NotImplementedError

    @abstractmethod
    async def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to session."""
        raise NotImplementedError

    @abstractmethod
    async def get_messages(self, session_id: str, limit: int = 10) -> List[Message]:
        """Get recent messages from session."""
        raise NotImplementedError

    @abstractmethod
    async def update_context(self, session_id: str, context: ConversationContext) -> None:
        """Update extracted context for session."""
        raise NotImplementedError

    @abstractmethod
    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get extracted context for session."""
        raise NotImplementedError

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        raise NotImplementedError

    @abstractmethod
    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        raise NotImplementedError


class InMemorySessionStore(BaseSessionStore):
    """In-memory session store implementation."""

    def __init__(self, ttl_minutes: int = 1440):
        """Initialize in-memory store.

        Args:
            ttl_minutes: Session time-to-live in minutes (default: 24 hours)
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Check TTL
        if datetime.utcnow() > session["expires_at"]:
            del self.sessions[session_id]
            return None

        return session

    async def create_session(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new session."""
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "messages": [],
            "context": ConversationContext(),
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.ttl,
        }
        self.sessions[session_id] = session
        return session

    async def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to session."""
        session = await self.get_session(session_id)
        if not session:
            await self.create_session(session_id)
            session = self.sessions[session_id]

        # Add message
        message = Message(role=role, content=content)
        session["messages"].append(message.model_dump())

        # Update expiration
        session["expires_at"] = datetime.utcnow() + self.ttl

    async def get_messages(self, session_id: str, limit: int = 10) -> List[Message]:
        """Get recent messages from session."""
        session = await self.get_session(session_id)
        if not session:
            return []

        messages = session["messages"][-limit:]
        return [Message(**msg) for msg in messages]

    async def update_context(self, session_id: str, context: ConversationContext) -> None:
        """Update extracted context for session."""
        session = await self.get_session(session_id)
        if not session:
            await self.create_session(session_id)
            session = self.sessions[session_id]

        session["context"] = context.model_dump()
        session["expires_at"] = datetime.utcnow() + self.ttl

    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get extracted context for session."""
        session = await self.get_session(session_id)
        if not session:
            return None

        context_data = session.get("context", {})
        return ConversationContext(**context_data)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return (await self.get_session(session_id)) is not None


class RedisSessionStore(BaseSessionStore):
    """Redis-backed session store implementation."""

    def __init__(self, redis_client: Any, ttl_minutes: int = 1440, prefix: str = "chat:"):
        """Initialize Redis store.

        Args:
            redis_client: Redis client instance (redis.asyncio.Redis)
            ttl_minutes: Session time-to-live in minutes
            prefix: Key prefix for session data
        """
        self.redis = redis_client
        self.ttl_seconds = ttl_minutes * 60
        self.prefix = prefix

    def _make_key(self, session_id: str, suffix: str = "") -> str:
        """Generate Redis key."""
        if suffix:
            return f"{self.prefix}{session_id}:{suffix}"
        return f"{self.prefix}{session_id}"

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data."""
        exists = await self.redis.exists(self._make_key(session_id))
        if not exists:
            return None

        # Retrieve session data
        messages_json = await self.redis.get(self._make_key(session_id, "messages"))
        context_json = await self.redis.get(self._make_key(session_id, "context"))

        messages = eval(messages_json) if messages_json else []
        context_data = eval(context_json) if context_json else {}

        return {
            "session_id": session_id,
            "messages": messages,
            "context": context_data,
        }

    async def create_session(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new session."""
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "messages": [],
            "context": ConversationContext().model_dump(),
        }

        # Store in Redis with TTL
        await self.redis.setex(
            self._make_key(session_id, "messages"),
            self.ttl_seconds,
            str([]),
        )
        await self.redis.setex(
            self._make_key(session_id, "context"),
            self.ttl_seconds,
            str(session["context"]),
        )

        return session

    async def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to session."""
        if not await self.session_exists(session_id):
            await self.create_session(session_id)

        # Get current messages
        messages_json = await self.redis.get(self._make_key(session_id, "messages"))
        messages = eval(messages_json) if messages_json else []

        # Add new message
        message = Message(role=role, content=content)
        messages.append(message.model_dump())

        # Store back with TTL
        await self.redis.setex(
            self._make_key(session_id, "messages"),
            self.ttl_seconds,
            str(messages),
        )

    async def get_messages(self, session_id: str, limit: int = 10) -> List[Message]:
        """Get recent messages from session."""
        messages_json = await self.redis.get(self._make_key(session_id, "messages"))
        if not messages_json:
            return []

        messages = eval(messages_json)[-limit:]
        return [Message(**msg) for msg in messages]

    async def update_context(self, session_id: str, context: ConversationContext) -> None:
        """Update extracted context for session."""
        if not await self.session_exists(session_id):
            await self.create_session(session_id)

        await self.redis.setex(
            self._make_key(session_id, "context"),
            self.ttl_seconds,
            str(context.model_dump()),
        )

    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get extracted context for session."""
        context_json = await self.redis.get(self._make_key(session_id, "context"))
        if not context_json:
            return None

        context_data = eval(context_json)
        return ConversationContext(**context_data)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        keys = [
            self._make_key(session_id, "messages"),
            self._make_key(session_id, "context"),
        ]
        result = await self.redis.delete(*keys)
        return result > 0

    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        exists = await self.redis.exists(self._make_key(session_id, "messages"))
        return exists > 0
