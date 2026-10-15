from app.memory.redis_memory import RedisMemory


class ConversationMemory(RedisMemory):
    """Backward-compatible name for the Redis conversation memory service."""


conversation_memory = ConversationMemory()
