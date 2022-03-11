from http import HTTPStatus

from flask import Blueprint, Response
from flask import abort, jsonify, request

import log
import run
from src import schemas
from src.exceptions import ResetPasswordTokenDecodeError, DBError
from src.models import User
from src.utils import decorators, request_helpers

logger = log.APILogger(__name__)

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.post('/register')
def register() -> Response:
    """Registers a new user via POST method"""
    logger.info('Got a new user registration request.')
    parsed_request_body = request_helpers.parse_reqeust_body_or_abort(request)

    user_info = request_helpers.get_validated_user_data_or_abort(
        schemas.register_user_schema,
        parsed_request_body
    )
    duplicate_id = User.get_duplicate_id(user_info)
    if duplicate_id:
        return abort(HTTPStatus.CONFLICT, f'User with the same info already exists. Id: {duplicate_id}')

    try:
        user = User.create_user(user_info)
    except DBError as e:
        return abort(HTTPStatus.INTERNAL_SERVER_ERROR, str(e))
    except Exception as e:
        logger.error(f'Failed to create a new user. Error type: {e}\nError: {e}')
        return abort(HTTPStatus.BAD_REQUEST, f'Can not create such user. Error: {e}')

    return jsonify({'msg': f'user {user} created!', 'id': user.id})


@users_bp.post('/forgot-password')
def forgot_password() -> Response:
    """Sends an email with refresh password instructions"""
    logger.info('Got a new forgot password request.')
    parsed_reqeust_body = request_helpers.parse_reqeust_body_or_abort(request)
    user_info = request_helpers.get_validated_user_data_or_abort(
        schemas.forgot_password_schema,
        parsed_reqeust_body
    )
    email_address = user_info['email_address']
    user = User.get_by_email_address(email_address)
    logger.info(f'Forgot password for {email_address}')
    if not user:
        abort(HTTPStatus.NOT_FOUND, f'User with email address {email_address} does not exists')

    token = run.reset_password_token_generator.create_token({'rid': user.id})
    run.email_sender.send_password_reset_email(
        user.email_address,
        token,
    )
    return jsonify({'msg': 'Recovery email was sent to your email.'})


@users_bp.post('/check-reset-password-token/<token>')
def check_reset_password_token(token: str) -> Response:
    """Validates a reset password token.

    Args:
        token (str): A reset password token from an email

    Returns:
       Response: A response with resetPasswordToken to be used by /reset-password endpoint.
    """
    try:
        data = run.reset_password_token_decoder.decode_token(token)
    except ResetPasswordTokenDecodeError as e:
        return abort(HTTPStatus.UNAUTHORIZED, f'{e}')

    try:
        user_id = data['rid']
    except KeyError:
        logger.error('Failed to get a record id from the token.')
        return abort(HTTPStatus.UNAUTHORIZED, 'Invalid token.')

    user = User.get_by_id(user_id)
    token = run.access_token_generator.create_token({'rid': user_id})
    if user:
        return jsonify({
            'msg': 'Token is valid.',
            'resetPasswordToken': token,
        })

    logger.error(f'Failed to fine a user with id: {user_id}')
    return abort(HTTPStatus.UNAUTHORIZED, 'Invalid token')


@users_bp.post('/reset-password')
@decorators.required_access_token
def reset_password(user: User) -> Response:
    """Resets a user password.

    Args:
        user (User): User object

    Returns:
        Response: Password rest status
    """
    logger.info('Got a new reqeust for password reset.')
    parsed_reqeust_body = request_helpers.parse_reqeust_body_or_abort(request)
    user_info = request_helpers.get_validated_user_data_or_abort(
        schemas.reset_password_schema,
        parsed_reqeust_body
    )

    user.password = user_info['password']
    try:
        user.save_to_db()
    except DBError as e:
        logger.error(e)
        return abort(HTTPStatus.INTERNAL_SERVER_ERROR, 'Failed to update password')

    logger.info(f'Password for the user {user.id} was updated')
    return jsonify({'msg': 'Password updated'})


@users_bp.get('/')
def home() -> Response:
    return jsonify({'msg': 'hello!'})


@users_bp.get('/private')
@decorators.required_access_token
def private(user: User) -> Response:
    return jsonify({'msg': f'private hello for user: {user}'})
