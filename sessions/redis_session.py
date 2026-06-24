"""Redis-backed OpenAI Agents SDK session and shared-client factories."""

from __future__ import annotations

from agents.extensions.memory import RedisSession
from redis.asyncio import Redis


async def create_redis_client(
    url: str,
    *,
    connect_timeout_seconds: float,
    socket_timeout_seconds: float,
    max_connections: int,
) -> Redis:
    """Create and verify a bounded async Redis client without retry storms."""
    client = Redis.from_url(
        url,
        decode_responses=False,
        socket_connect_timeout=connect_timeout_seconds,
        socket_timeout=socket_timeout_seconds,
        max_connections=max_connections,
        retry_on_timeout=False,
        health_check_interval=30,
    )
    try:
        await client.ping()
    except BaseException:
        await client.aclose()
        raise
    return client


def create_redis_session(
    session_id: str,
    client: Redis,
    ttl_seconds: int,
    key_prefix: str,
) -> RedisSession:
    """Create a Redis session that reuses the process-owned connection pool."""
    return RedisSession(
        session_id=session_id,
        redis_client=client,
        ttl=ttl_seconds,
        key_prefix=key_prefix,
    )
