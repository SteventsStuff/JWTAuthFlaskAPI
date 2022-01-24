from http import HTTPStatus

import jwt
from flask import Blueprint, request, jsonify, Response, abort, make_response

import run
from src.utils import request_helpers, decorators
from src.models import User
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.post('/login')
def login() -> Response:
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            jsonify({'msg': 'Could not verify creds'}),
            HTTPStatus.UNAUTHORIZED,
            {'WWW-Authenticate': 'Basic realm="Authentication Failed"'}
        )

    user = User.query.filter_by(username=auth.username).first()
    if not user or not check_password_hash(user.password, auth.password):
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
    return jsonify(response)


@auth_bp.post('/social-login')
def social_login() -> Response:
    pass


@auth_bp.post('/refresh')
def refresh() -> Response:
    parsed_request_body = request_helpers.parse_reqeust_body_or_abort(request)
    try:
        refresh_token = parsed_request_body['refreshToken']
    except KeyError:
        return abort(HTTPStatus.UNAUTHORIZED, 'invalid refresh token')

    try:
        run.jwt_decoder.decode_token(refresh_token)
    except jwt.InvalidTokenError:  # todo: create custom exception for that in JWTHelper
        return abort(HTTPStatus.UNAUTHORIZED, 'invalid refresh token')

    user_id = run.refresh_token_storage_controller.get_user_id_by_refresh_token(refresh_token)
    if not user_id:
        return abort(HTTPStatus.UNAUTHORIZED, 'invalid refresh token')

    access_token = run.access_token_generator.create_token({'rid': user_id})
    new_refresh_token = run.refresh_token_generator.create_token()
    run.refresh_token_storage_controller.reset_user_refresh_token(refresh_token, new_refresh_token)

    response = {
        'accessToken': access_token,
        'refreshToken': new_refresh_token,
    }
    return jsonify(response)


@auth_bp.delete('/logout')
@decorators.required_access_token
def logout(user: User) -> Response:
    run.refresh_token_storage_controller.remove_refresh_token(user.id)
    return make_response('', HTTPStatus.NO_CONTENT)
