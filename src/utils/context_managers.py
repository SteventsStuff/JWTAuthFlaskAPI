from redis import Redis


class RedisContextManager:
    """Context manager for a redis connector"""
    def __init__(self, host: str, port: int, db: int) -> None:
        self._redis = Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )

    def __enter__(self) -> Redis:
        return self._redis

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._redis.close()

        if exc_type:
            raise exc_type
