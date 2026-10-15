import json
from typing import Any

from redis import Redis

from app.core.config import settings


class RedisMemory:
    """Manage conversation history and booking drafts in Redis."""

    def __init__(self, client: Redis | None = None) -> None:
        self.client = client or Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

    @staticmethod
    def _conversation_key(session_id: str) -> str:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty.")
        return f"conversation:{session_id}"

    @staticmethod
    def _draft_key(session_id: str) -> str:
        if not session_id.strip():
            raise ValueError("Session ID cannot be empty.")
        return f"booking_draft:{session_id}"

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        """Return stored conversation messages in chronological order."""
        messages = self.client.lrange(
            self._conversation_key(session_id), 0, -1
        )
        return [json.loads(message) for message in messages]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """Append a message and refresh the conversation's TTL."""
        if role not in {"user", "assistant", "system"}:
            raise ValueError("Unsupported conversation role.")

        key = self._conversation_key(session_id)
        self.client.rpush(
            key,
            json.dumps({"role": role, "content": content}),
        )
        self.client.expire(key, 86400)

    def clear_history(self, session_id: str) -> None:
        """Delete conversation history for a session."""
        self.client.delete(self._conversation_key(session_id))

    def get_booking_draft(self, session_id: str) -> dict[str, Any] | None:
        """Return an in-progress booking draft, if present."""
        value = self.client.get(self._draft_key(session_id))
        return json.loads(value) if value is not None else None

    def save_booking_draft(
        self,
        session_id: str,
        draft: dict[str, Any],
    ) -> None:
        """Save a booking draft for 24 hours."""
        self.client.set(
            self._draft_key(session_id),
            json.dumps(draft),
            ex=86400,
        )

    def clear_booking_draft(self, session_id: str) -> None:
        """Delete a booking draft."""
        self.client.delete(self._draft_key(session_id))

    def health_check(self) -> bool:
        """Return whether Redis responds to a ping."""
        return bool(self.client.ping())


redis_memory = RedisMemory()
