import uuid

import redis.asyncio as redis

from .base import DeduplicationBackend


class RedisDeduplicationBackend(DeduplicationBackend):
    def __init__(self, url: str, **connection_kwargs):
        super().__init__()
        self.connection_pool = redis.BlockingConnectionPool.from_url(
            url, **connection_kwargs
        )

    async def set_message_id(self, task_id: str, message_id: str):
        async with redis.Redis(connection_pool=self.connection_pool, decode_responses=True) as conn:
            await conn.set(self._get_key(task_id), message_id)

    async def get_message_id(self, task_id: str) -> str | None:
        async with redis.Redis(connection_pool=self.connection_pool, decode_responses=True) as conn:
            value = await conn.get(self._get_key(task_id))

            match value:
                case str() | None:
                    return value
                case bytes():
                    return value.decode("utf-8")
                case _:
                    raise

    def next_message_id(self) -> str:
        return str(uuid.uuid4())

    def _get_key(self, task_id: str) -> str:
        return f"__dedup_{task_id}"
