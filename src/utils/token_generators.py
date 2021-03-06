import datetime
import typing as t

import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as JSONSerializer

import log
from src.abstractions.abc_token_generator import ABCTokenGenerator
from src.exceptions import AccessTokenGeneratorError, ResetPasswordTokenGeneratorError
from src.mixins import ExpirationTimeMixin

logger = log.APILogger(__name__)


class AccessTokenGenerator(ABCTokenGenerator, ExpirationTimeMixin):
    def __init__(self, config=None) -> None:
        self._app_config = config or None

    def create_token(self, claims: t.Dict[str, t.Any]) -> str:
        """Creates an access JWT based on claims

        Args:
            claims (dict): JWT claims

        Returns:
            str: JWT
        """
        logger.info('Creating a new JWT access token...')
        try:
            record_id = claims['rid']
        except KeyError as e:
            raise AccessTokenGeneratorError(
                f'Claims must contain {e} field to generate access token'
            )
        payload = self._create_jwt_access_payload(record_id)
        token = jwt.encode(payload, self._app_config['SECRET_KEY'])
        return token

    def _create_jwt_access_payload(
            self,
            record_id: int,
            additional_claims: t.Dict[str, t.Any] = None
    ) -> t.Dict[str, t.Any]:
        token_exp_timeout = self._app_config['JWT_ACCESS_TOKEN_EXPIRATION']
        issuer = self._app_config['JWT_ISSUER'] or self._app_config['SERVER_NAME']
        issued_at = datetime.datetime.utcnow()
        payload = {
            'rid': record_id,
            'iss': issuer,
            'iat': issued_at,
            'exp': self.create_exp_timestamp(issued_at, token_exp_timeout),
        }
        if additional_claims:
            additional_claims.pop('iat')
            additional_claims.pop('exp')
            payload.update(additional_claims)
        return payload


class RefreshTokenGenerator(ABCTokenGenerator, ExpirationTimeMixin):
    def __init__(self, config=None) -> None:
        self._app_config = config or None

    def create_token(self, claims: t.Dict[str, t.Any] = None) -> str:
        """Creates a refresh JWT based on claims

       Args:
           claims (dict): JWT claims

       Returns:
           str: JWT
       """
        logger.info('Creating a new JWT refresh token...')
        payload = self._create_jwt_refresh_payload(claims)
        token = jwt.encode(payload, self._app_config['SECRET_KEY'])
        return token

    def _create_jwt_refresh_payload(
            self,
            additional_claims: t.Dict[str, t.Any] = None
    ) -> t.Dict[str, t.Any]:
        token_exp_timeout = self._app_config['JWT_REFRESH_TOKEN_EXPIRATION']
        issuer = self._app_config['JWT_ISSUER'] or self._app_config['SERVER_NAME']
        issued_at = datetime.datetime.utcnow()
        payload = {
            'iss': issuer,
            'iat': issued_at,
            'exp': self.create_exp_timestamp(issued_at, token_exp_timeout),
        }
        if additional_claims:
            additional_claims.pop('rid')
            additional_claims.pop('iat')
            additional_claims.pop('exp')
            payload.update(additional_claims)
        return payload


class ResetPasswordTokenGenerator(ABCTokenGenerator):
    def __init__(self, config=None):
        self._app_config = config or None
        self._serializer: JSONSerializer = JSONSerializer(
            self._app_config['SECRET_KEY'],
            expires_in=self._app_config['MAIL_EXPIRES_IN']
        )

    def create_token(self, claims: t.Dict[str, t.Any]) -> str:
        """Creates a rest password token based on claims

        Args:
            claims (dict): token claims

        Returns:
            str: rest password token
        """
        logger.info('Creating a new password refresh token...')
        try:
            user_id = claims['rid']
        except KeyError as e:
            raise ResetPasswordTokenGeneratorError(
                f'Claims must contain {e} field to generate token'
            )
        return self._serializer.dumps({'rid': user_id}).decode('utf-8')
