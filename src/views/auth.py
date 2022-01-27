from http import HTTPStatus

import jwt
from flask import Blueprint, request, jsonify, Response, abort, make_response

import run
import log
from src.utils import request_helpers, decorators
from src.models import User
from werkzeug.security import check_password_hash

logger = log.APILogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.post('/login')
def login() -> Response:
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        msg = 'Failed to log in'
        msg = f'{msg} with username: {auth.username}.' if auth.username else f'{msg}.'
        logger.error(msg)
        return make_response(
            jsonify({'msg': 'Could not verify creds.'}),
            HTTPStatus.UNAUTHORIZED,
            {'WWW-Authenticate': 'Basic realm="Authentication Failed"'}
        )

    user = User.query.filter_by(username=auth.username).first()
    if not user or not check_password_hash(user.password, auth.password):
        logger.error(f'User ({auth.username}) provided incorrect password.')
        return make_response(
            jsonify({'msg': 'Could not verify creds'}),
            HTTPStatus.UNAUTHORIZED,
            {'WWW-Authenticate': 'Basic realm="Authentication Failed"'}
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


@auth_bp.post('/social-login')
def social_login() -> Response:
    pass


@auth_bp.post('/refresh')
def refresh() -> Response:
    logger.info(f'Got a new request for a token refresh')
    parsed_request_body = request_helpers.parse_reqeust_body_or_abort(request)
    try:
        refresh_token = parsed_request_body['refreshToken']
    except KeyError as e:
        logger.error(f'Request body does not contain a mandatory field {e}')
        return abort(HTTPStatus.UNAUTHORIZED, 'Invalid refresh token')

    try:
        run.jwt_decoder.decode_token(refresh_token)
    except jwt.InvalidTokenError as e:
        logger.error(f'Failed to decode token: {e}')
        return abort(HTTPStatus.UNAUTHORIZED, 'Invalid refresh token')

    user_id = run.refresh_token_storage_controller.get_user_id_by_refresh_token(refresh_token)
    if not user_id:
        logger.error(f'User was not found by a token.')
        return abort(HTTPStatus.UNAUTHORIZED, 'Invalid refresh token')

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
def logout(user: User) -> Response:
    run.refresh_token_storage_controller.remove_refresh_token(user.id)
    logger.info(f'{user} was logged out.')
    return make_response('', HTTPStatus.NO_CONTENT)
