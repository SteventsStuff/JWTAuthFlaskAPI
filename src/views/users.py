from http import HTTPStatus

from flask import Blueprint, Response, abort, jsonify, request

import run
from src import schemas
from src.models import User
from src.utils import decorators, request_helpers
from src.exceptions import ResetPasswordTokenDecodeError, DBError

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.post('/register')
def register() -> Response:
    parsed_request_body = request_helpers.parse_reqeust_body_or_abort(request)

    user_info = request_helpers.get_validated_user_data_or_abort(
        schemas.register_user_schema,
        parsed_request_body
    )
    duplicate_id = User.is_already_exists(user_info)
    if duplicate_id:
        abort(HTTPStatus.CONFLICT, f'User with the same info already exists. Id: {duplicate_id}')

    user = User.create(user_info)
    try:
        user.save_to_db()
    except DBError as e:
        print(e)
        return abort(HTTPStatus.INTERNAL_SERVER_ERROR, str(e))

    return jsonify({'msg': f'user {user} created!', 'id': user.id})


@users_bp.post('/forgot-password')
def forgot_password() -> Response:
    parsed_reqeust_body = request_helpers.parse_reqeust_body_or_abort(request)
    user_info = request_helpers.get_validated_user_data_or_abort(
        schemas.forgot_password_schema,
        parsed_reqeust_body
    )
    email_address = user_info['email_address']
    user = User.get_by_email_address(email_address)
    if not user:
        abort(HTTPStatus.NOT_FOUND, f'User with email address {email_address} does not exists')

    token = run.reset_password_token_generator.create_token({'rid': user.id})
    run.email_sender.send_password_reset_email(
        user.email_address,
        token,
    )
    return jsonify({'msg': 'Recovery email was sent to your email.'})


@users_bp.post('/reset-password')
@decorators.required_access_token
def reset_password(user: User) -> Response:
    parsed_reqeust_body = request_helpers.parse_reqeust_body_or_abort(request)
    user_info = request_helpers.get_validated_user_data_or_abort(
        schemas.reset_password_schema,
        parsed_reqeust_body
    )

    user.password = user_info['password']
    try:
        user.save_to_db()
    except DBError as e:
        print(e)
        return abort(HTTPStatus.INTERNAL_SERVER_ERROR, 'Failed to update password')

    return jsonify({'msg': 'Password updated'})


@users_bp.post('/check-reset-password-token/<token>')
def check_reset_password_token(token: str) -> Response:
    try:
        data = run.reset_password_token_decoder.decode_token(token)
    except ResetPasswordTokenDecodeError as e:
        return abort(HTTPStatus.UNAUTHORIZED, f'{e}')

    try:
        user_id = data['rid']
    except KeyError:
        return abort(HTTPStatus.UNAUTHORIZED, 'Invalid token.')

    user = User.get_by_id(user_id)
    token = run.access_token_generator.create_token({'rid': user_id})
    if user:
        return jsonify({
            'msg': 'Token is valid.',
            'resetPasswordToken': token,
        })

    return abort(HTTPStatus.UNAUTHORIZED, 'Invalid token')


@users_bp.get('/')
def home() -> Response:
    return jsonify({'msg': 'hello!'})


@users_bp.get('/private')
@decorators.required_access_token
def private(user: User) -> Response:
    return jsonify({'msg': 'private hello!'})
