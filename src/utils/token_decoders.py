import typing as t

import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as JSONSerializer
from itsdangerous.exc import BadData

import log
from src.abstractions.abc_token_decoder import ABCTokenDecoder
from src.exceptions import ResetPasswordTokenDecodeError

logger = log.APILogger(__name__)


class JWTDecoder(ABCTokenDecoder):

    def __init__(self, config: t.Dict[str, t.Any] = None) -> None:
        self._app_config = config or None

    def decode_token(self, token: str) -> str:
        """Decodes a JWT

        Args:
            token (str): JWT

        Returns:
            str: decoded token
        """

        logger.info('Trying to decode a JWT token...')
        return jwt.decode(token, self._app_config['SECRET_KEY'], [self._app_config['JWT_ALGORITHM']])


class ResetPasswordTokenDecoder(ABCTokenDecoder):

    def __init__(self, config: t.Dict[str, t.Any] = None) -> None:
        self._app_config = config or None
        self._serializer: JSONSerializer = JSONSerializer(
            self._app_config['SECRET_KEY'],
            expires_in=self._app_config['MAIL_EXPIRES_IN']
        )

    def decode_token(self, token: str) -> t.Dict[str, str]:
        """Decodes JWS JSON Web Signature (JWS).

        Args:
            token (str): JWS token

        Returns:
            dict: user information

        Raises:
            ResetPasswordTokenDecodeError: if invalid token specified
        """

        logger.info('Trying to decode a password refresh token...')
        try:
            return self._serializer.loads(token)
        except BadData as e:
            print(e)
            raise ResetPasswordTokenDecodeError('Invalid token') from e
