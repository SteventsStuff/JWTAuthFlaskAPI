import typing as t

import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as JSONSerializer
from itsdangerous.exc import BadData

from src.abstractions.abc_token_decoder import ABCTokenDecoder
from src.exceptions import ResetPasswordTokenDecodeError


class JWTDecoder(ABCTokenDecoder):
    def __init__(self, config=None):
        self._app_config = config or None

    def decode_token(self, token: str) -> str:
        return jwt.decode(token, self._app_config['SECRET_KEY'], [self._app_config['JWT_ALGORITHM']])


class ResetPasswordTokenDecoder(ABCTokenDecoder):
    def __init__(self, config=None):
        self._app_config = config or None
        self._serializer: JSONSerializer = JSONSerializer(
            self._app_config['SECRET_KEY'],
            expires_in=self._app_config['MAIL_EXPIRES_IN']
        )

    def decode_token(self, token: str) -> t.Dict[str, str]:
        try:
            return self._serializer.loads(token)
        except BadData as e:
            print(e)
            raise ResetPasswordTokenDecodeError('Invalid token') from e
