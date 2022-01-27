import typing as t
from .context_managers import RedisContextManager


class RefreshTokenStorageController:
    _KEY_NAME: str = 'refreshTokens'

    def __init__(self, host: str, port: int, db: int):
        self._host: str = host
        self._port: int = port
        self._db: int = db

    def get_user_id_by_refresh_token(self, token: str) -> t.Optional[str]:
        with RedisContextManager(self._host, self._port, self._db) as redis_conn:
            user_id = redis_conn.hget(self._KEY_NAME, token)
        return user_id

    def set_user_refresh_token(self, user_id: str, token: str) -> None:
        with RedisContextManager(self._host, self._port, self._db) as redis_conn:
            data = redis_conn.hgetall(self._KEY_NAME)
            existing_token = self._find_key_by_value(data, user_id)
            if existing_token:
                redis_conn.hdel(self._KEY_NAME, existing_token)
            redis_conn.hsetnx(self._KEY_NAME, token, user_id)

    def reset_user_refresh_token(self, current_token: str, new_token: str) -> None:
        with RedisContextManager(self._host, self._port, self._db) as redis_conn:
            user_id = redis_conn.hget(self._KEY_NAME, current_token)
            redis_conn.hdel(self._KEY_NAME, current_token)
            redis_conn.hsetnx(self._KEY_NAME, new_token, user_id)

    def remove_refresh_token(self, user_id: str) -> None:
        with RedisContextManager(self._host, self._port, self._db) as redis_conn:
            data = redis_conn.hgetall(self._KEY_NAME)
            token_to_delete = self._find_key_by_value(data, user_id)
            if token_to_delete:
                redis_conn.hdel(self._KEY_NAME, token_to_delete)

    @staticmethod
    def _find_key_by_value(data: t.Dict[str, str], value: str) -> t.Optional[str]:
        values = list(data.values())
        keys = list(data.keys())
        try:
            index = values.index(value)
        except ValueError:
            return None
        return keys[index]
