import typing as t

from .context_managers import RedisContextManager


class RefreshTokenStorageController:
    _KEY_NAME: str = 'refreshTokens'

    def __init__(self, host: str, port: int, db: int, password: str = '') -> None:
        self._host: str = host
        self._port: int = port
        self._password: str = password
        self._db: int = db
        #
        self._context_manager_context = {
            'host': self._host,
            'port': self._port,
            'password': self._password,
            'db': self._db,
        }

    def get_user_id_by_refresh_token(self, refresh_token: str) -> t.Optional[str]:
        """Gets a user id from Redis by refresh token

        Args:
            refresh_token (str): Token

        Returns:
            str: User id
        """
        with RedisContextManager(**self._context_manager_context) as redis_conn:
            user_id = redis_conn.hget(self._KEY_NAME, refresh_token)
        return user_id

    def set_user_refresh_token(self, user_id: str, refresh_token: str) -> None:
        """Sets a new user refresh token in Redis

        Args:
            user_id (str): User id
            refresh_token (str): Refresh token

        Returns:
            None
        """
        with RedisContextManager(**self._context_manager_context) as redis_conn:
            data = redis_conn.hgetall(self._KEY_NAME)
            existing_token = self._find_key_by_value(data, user_id)
            if existing_token:
                redis_conn.hdel(self._KEY_NAME, existing_token)
            redis_conn.hsetnx(self._KEY_NAME, refresh_token, user_id)

    def reset_user_refresh_token(self, current_refresh_token: str, new_refresh_token: str) -> None:
        """Replaces current refresh token by a new token in Redis

        Args:
            current_refresh_token (str): Current refresh token
            new_refresh_token (str): New refresh token

        Returns:
            None
        """
        with RedisContextManager(**self._context_manager_context) as redis_conn:
            user_id = redis_conn.hget(self._KEY_NAME, current_refresh_token)
            redis_conn.hdel(self._KEY_NAME, current_refresh_token)
            redis_conn.hsetnx(self._KEY_NAME, new_refresh_token, user_id)

    def remove_refresh_token(self, user_id: str) -> None:
        """Removes refresh token from Redis

        Args:
            user_id (str): User id

        Returns:
            None
        """
        with RedisContextManager(**self._context_manager_context) as redis_conn:
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
