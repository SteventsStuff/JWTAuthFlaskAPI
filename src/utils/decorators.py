import typing as t
import functools
from http import HTTPStatus

import jwt
from flask import request, abort, Response

import run
import src.utils.request_helpers as helpers
from src.models import User


def required_access_token(func: t.Callable) -> t.Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Response:
        token = helpers.get_bearer_auth_token(request)

        if not token:
            return abort(HTTPStatus.UNAUTHORIZED, 'Token is required!')

        try:
            data = run.jwt_decoder.decode_token(token)
            user_id = data.get('rid')
            user = User.query.filter_by(id=user_id).first()
        except jwt.DecodeError as e:
            print(e)
            return abort(HTTPStatus.UNAUTHORIZED, f'{e}')
        except jwt.ExpiredSignatureError as e:
            print(e)
            return abort(HTTPStatus.UNAUTHORIZED, f'{e}')
        except Exception as e:
            print(e)
            return abort(HTTPStatus.INTERNAL_SERVER_ERROR, 'INTERNAL SERVER ERROR...')
        else:
            # in case if use was deleted (somehow, lol)
            if not user:
                abort(HTTPStatus.UNAUTHORIZED, f'Invalid user')

        return func(user, *args, **kwargs)

    return wrapper
