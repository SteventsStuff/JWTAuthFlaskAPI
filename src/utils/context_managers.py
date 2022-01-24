from redis import Redis


class RedisContextManager:
    def __init__(self, host: str, port: int, db: int) -> None:
        self._redis = Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )

    def __enter__(self) -> Redis:
        return self._redis

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._redis.close()
        if exc_type:
            print(f'{exc_type}: {exc_val}\n{exc_tb}')
            raise exc_type
