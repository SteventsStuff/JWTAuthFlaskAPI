import functools
import typing as t
from http import HTTPStatus

import jwt
from flask import request, abort, Response

import log
import run
import src.utils.request_helpers as helpers
from src.models import User

logger = log.APILogger(__name__)


def required_access_token(func: t.Callable) -> t.Callable:
    """Decorates a view function to add an auth by JWT

    Args:
        func (callable): View function

    Returns:
        callable: A decorated view function that required a JWT auth
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        token = helpers.get_bearer_auth_token(request)

        if not token:
            logger.error('Token was not provided')
            return abort(HTTPStatus.UNAUTHORIZED, 'Token is required!')

        try:
            data = run.jwt_decoder.decode_token(token)
            user_id = data.get('rid')
            user = User.query.filter_by(id=user_id, ).first()
        except (jwt.DecodeError, jwt.ExpiredSignatureError) as e:
            logger.warning(e)
            return abort(HTTPStatus.UNAUTHORIZED, f'{e}')
        except Exception as e:
            logger.error(e)
            return abort(HTTPStatus.INTERNAL_SERVER_ERROR, 'INTERNAL SERVER ERROR...')
        else:
            # in case if use was deleted (somehow, lol)
            if not user:
                logger.error(f'User with id: {user_id} does not exist or inactive')
                abort(HTTPStatus.UNAUTHORIZED, f'Invalid user')

        return func(user, *args, **kwargs)

    return wrapper
