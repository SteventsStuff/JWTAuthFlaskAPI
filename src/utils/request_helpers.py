import typing as t
from http import HTTPStatus

from flask import Request as FlaskRequest
from flask import abort
from marshmallow import ValidationError
from requests import Response

import log
from src.schemas import ma

logger = log.APILogger(__name__)


def parse_reqeust_body_or_abort(request_obj: t.Union[FlaskRequest, Response]) -> t.Dict[t.Any, t.Any]:
    """Parses a request response body.

    Args:
        request_obj (union[FlaskRequest, Response]): Reqeust object

    Returns:
        dict: Response data
    """

    logger.info('Trying to parse reqeust body...')
    try:
        if isinstance(request_obj, FlaskRequest):
            parsed_reqeust_body = request_obj.json
        else:
            parsed_reqeust_body = request_obj.json()
    except ValueError as e:
        logger.error(f'Failed to parse reqeust body. Error: {e}')
        return abort(HTTPStatus.BAD_REQUEST, 'Failed to parse reqeust body')

    if not parsed_reqeust_body:
        logger.error(f'Got empty request body.')
        return abort(HTTPStatus.BAD_REQUEST, 'Empty data is invalid')

    return parsed_reqeust_body


def get_validated_user_data_or_abort(
        schema: ma.Schema,
        request_body: t.Dict[str, t.Any]
) -> t.Dict[str, t.Any]:
    """Validates a response body with a marshmallow schema

    Args:
        schema (Schema): Marshmallow schema
        request_body (dict): Request body

    Returns:
        dict: Validated request body
    """

    logger.info('Validating reqeust body...')
    try:
        return schema.load(request_body)
    except ValidationError as e:
        logger.error('Failed to validate reqeust')
        return abort(HTTPStatus.BAD_REQUEST, e.args[0])


def get_bearer_auth_token(request_obj: FlaskRequest) -> t.Optional[str]:
    """Extracts a token from a bearer auth

    Args:
        request_obj (Request): reqeust body

    Returns:
        str: Token
    """
    auth_header = request_obj.headers.get('Authorization', '')
    splitted_header_value = auth_header.split('Bearer ')
    token = splitted_header_value[-1] if len(splitted_header_value) == 2 else None
    return token
