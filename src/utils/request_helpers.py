import typing as t
from http import HTTPStatus

from flask import request, abort
from marshmallow import ValidationError

from src.schemas import ma


def parse_reqeust_body_or_abort(request_obj: request) -> t.Dict[t.Any, t.Any]:
    try:
        parsed_reqeust_body = request_obj.json
    except ValueError:
        return abort(HTTPStatus.BAD_REQUEST, 'Failed to parse reqeust body')

    if not parsed_reqeust_body:
        return abort(HTTPStatus.BAD_REQUEST, 'Empty data is invalid')

    return parsed_reqeust_body


def get_validated_user_data_or_abort(schema: ma.Schema,
                                     request_body: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    try:
        return schema.load(request_body)
    except ValidationError as e:
        return abort(HTTPStatus.BAD_REQUEST, e.args[0])


def get_bearer_auth_token(request_obj: request) -> t.Optional[str]:
    auth_header = request_obj.headers.get('Authorization', '')
    splitted_header_value = auth_header.split('Bearer ')
    token = splitted_header_value[-1] if len(splitted_header_value) == 2 else None
    return token
