from http import HTTPStatus

import jwt
from flask import Blueprint
from flask import Response as FlaskResponse
from flask import request, jsonify, abort, make_response
from werkzeug.security import check_password_hash

import log
import run
from src.models import User
from src.utils import request_helpers, decorators

logger = log.APILogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

WWW_AUTHENTICATE: str = 'WWW-Authenticate'
AUTH_FAILED_REALM: str = 'Authentication Failed'
INVALID_TOKEN_MSG: str = 'Invalid refresh token'


@auth_bp.post('/login')
def login() -> FlaskResponse:
    """Login a user by the Basic Auth (login and password)

    Notes:
        UNAUTHORIZED (401) response if token is invalid

    Returns:
        Response: A response with access and refresh tokens
    """
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        msg = 'Failed to log in'
        msg = f'{msg} with username: {auth.username}.' if auth.username else f'{msg}.'
        logger.error(msg)
        return make_response(
            jsonify({'msg': 'Could not verify creds.'}),
            HTTPStatus.UNAUTHORIZED,
            {WWW_AUTHENTICATE: f'Basic realm="{AUTH_FAILED_REALM}"'}
        )

    user = User.query.filter_by(username=auth.username).first()
    if not user or not check_password_hash(user.password, auth.password):
        logger.error(f'User ({auth.username}) provided incorrect password.')
        return make_response(
            jsonify({'msg': 'Could not verify creds'}),
            HTTPStatus.UNAUTHORIZED,
            {WWW_AUTHENTICATE: f'Basic realm="{AUTH_FAILED_REALM}"'}
        )
    access_token = run.access_token_generator.create_token({'rid': user.id})
    refresh_token = run.refresh_token_generator.create_token()
    run.refresh_token_storage_controller.set_user_refresh_token(user.id, refresh_token)

    response = {
        'accessToken': access_token,
        'refreshToken': refresh_token,
    }
    logger.info(f'User {user.username} successfully logged in.')
    return jsonify(response)


@auth_bp.post('/refresh')
def refresh() -> FlaskResponse:
    """Refreshes user's access and refresh token

    Returns:
        Response: A response with new access and refresh tokens
    """
    logger.info(f'Got a new request for a token refresh')
    parsed_request_body = request_helpers.parse_reqeust_body_or_abort(request)
    try:
        refresh_token = parsed_request_body['refreshToken']
    except KeyError as e:
        logger.error(f'Request body does not contain a mandatory field {e}')
        return abort(HTTPStatus.UNAUTHORIZED, INVALID_TOKEN_MSG)

    try:
        run.jwt_decoder.decode_token(refresh_token)
    except jwt.InvalidTokenError as e:
        logger.error(f'Failed to decode token: {e}')
        return abort(HTTPStatus.UNAUTHORIZED, INVALID_TOKEN_MSG)

    user_id = run.refresh_token_storage_controller.get_user_id_by_refresh_token(refresh_token)
    if not user_id:
        logger.error(f'User was not found by a token.')
        return abort(HTTPStatus.UNAUTHORIZED, INVALID_TOKEN_MSG)

    access_token = run.access_token_generator.create_token({'rid': user_id})
    new_refresh_token = run.refresh_token_generator.create_token()
    run.refresh_token_storage_controller.reset_user_refresh_token(refresh_token, new_refresh_token)

    response = {
        'accessToken': access_token,
        'refreshToken': new_refresh_token,
    }
    logger.info(f'Tokens were refreshed for user with id: {user_id}')
    return jsonify(response)


@auth_bp.delete('/logout')
@decorators.required_access_token
def logout(user: User) -> FlaskResponse:
    """Logout a user by removing a user's refresh token from Redis

    Args:
        user (User): User object

    Returns:
        Response: A response with NO CONTENT (204)
    """
    run.refresh_token_storage_controller.remove_refresh_token(user.id)
    logger.info(f'{user} was logged out.')
    return make_response('', HTTPStatus.NO_CONTENT)
