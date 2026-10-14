
import json

from redis import Redis

from app.core.config import settings


class ConversationMemory:
    """Store and retrieve conversation history using Redis."""

    def __init__(self) -> None:
        self.client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        key = f"conversation:{session_id}"
        messages = self.client.lrange(key, 0, -1)

        return [json.loads(message) for message in messages]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        key = f"conversation:{session_id}"

        self.client.rpush(
            key,
            json.dumps({"role": role, "content": content}),
        )

        # Automatically expire inactive conversations after 24 hours.
        self.client.expire(key, 86400)

    def clear_history(self, session_id: str) -> None:
        self.client.delete(f"conversation:{session_id}")

    def health_check(self) -> bool:
        return bool(self.client.ping())


    def get_booking_draft(self, session_id: str) -> dict | None:
        """Retrieve an in-progress booking draft."""
        key = f"booking_draft:{session_id}"
        draft = self.client.get(key)
        if draft is None:
            return None
        return json.loads(draft)

    def save_booking_draft(
        self,
        session_id: str,
        draft: dict,
    ) -> None:
        """Persist an in-progress booking draft for 24 hours."""
        key = f"booking_draft:{session_id}"
        self.client.set(
            key,
            json.dumps(draft),
            ex=86400,
        )

    def clear_booking_draft(self, session_id: str) -> None:
        """Remove a booking draft after completion or cancellation."""
        self.client.delete(f"booking_draft:{session_id}")



conversation_memory = ConversationMemory()
