from http import HTTPStatus

from flask import Blueprint
from flask import Response as FlaskResponse
from flask import jsonify, abort, url_for

import log
import run
from src.exceptions import DBError
from src.models import User
from src.utils import GoogleProfileMapper
from src.utils import request_helpers

logger = log.APILogger(__name__)

social_auth_bp = Blueprint('social_auth', __name__, url_prefix='/auth')


@social_auth_bp.get('/login/google')
def google_login() -> FlaskResponse:
    """Triggers a google auth redirect"""
    redirect_uri = url_for('social_auth.authorize_google', _external=True)
    return run.google_login_util.authorize_redirect(redirect_uri)


@social_auth_bp.get('/login/google/authorize')
def authorize_google() -> FlaskResponse:
    """Auth via Google

    Returns:
        Response: a response with new access and refresh tokens
    """
    # token = run.google_login_util.authorize_access_token()
    run.google_login_util.authorize_access_token()

    response = run.google_login_util.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = request_helpers.parse_reqeust_body_or_abort(response)
    email = user_info['email']

    user = User.get_by_email_address(email)
    if not user:
        mapper = GoogleProfileMapper(user_info)
        payload = mapper.create_payload()
        try:
            user = User.create_user(payload)
        except DBError as e:
            return abort(HTTPStatus.INTERNAL_SERVER_ERROR, str(e))
        except Exception as e:
            logger.error(f'Failed to create a new user. Error type: {e}\nError: {e}')
            return abort(HTTPStatus.BAD_REQUEST, f'Can not create such user. Error: {e}')
        else:
            logger.info(f'A new user {user.username} successfully created')

    access_token = run.access_token_generator.create_token({'rid': user.id})
    refresh_token = run.refresh_token_generator.create_token()
    run.refresh_token_storage_controller.set_user_refresh_token(user.id, refresh_token)

    response = {
        'accessToken': access_token,
        'refreshToken': refresh_token,
    }
    logger.info(f'User {user.username} successfully logged in.')
    return jsonify(response)
