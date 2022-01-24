from http import HTTPStatus
from typing import Tuple
from enum import Enum, unique

from flask import jsonify, Response
from werkzeug import exceptions as exc


@unique
class ResponseStatuses(Enum):
    failed = 'FAILED'


# 4xx
def bad_request(e: exc.BadRequest) -> Tuple[Response, int]:
    context = {
        'status': ResponseStatuses.failed.value,
        'message': 'Invalid request body was provided.',
        'details': e.description,
    }
    return jsonify(context), HTTPStatus.BAD_REQUEST


def unauthorized(e: exc.Unauthorized) -> Tuple[Response, int]:
    context = {
        'status': ResponseStatuses.failed.value,
        'message': 'Unauthorized',
        'details': e.description,
    }
    return jsonify(context), HTTPStatus.UNAUTHORIZED


def page_not_found(e: exc.NotFound) -> Tuple[Response, int]:
    context = {
        'status': ResponseStatuses.failed.value,
        'message': 'Not found.',
        'details': e.description,
    }
    return jsonify(context), HTTPStatus.NOT_FOUND


def method_not_allowed(e: exc.MethodNotAllowed) -> Tuple[Response, int]:
    context = {
        'status': ResponseStatuses.failed.value,
        'message': 'The method is not allowed for the requested URL.',
        'details': e.description,
    }
    return jsonify(context), HTTPStatus.METHOD_NOT_ALLOWED


def conflict(e: exc.Conflict) -> Tuple[Response, int]:
    context = {
        'status': ResponseStatuses.failed.value,
        'message': 'Can not process request...',
        'details': e.description,
    }
    return jsonify(context), HTTPStatus.CONFLICT


def unprocessed_entity(e: exc.UnprocessableEntity) -> Tuple[Response, int]:
    context = {
        'status': ResponseStatuses.failed.value,
        'message': 'Can not process provided data.',
        'details': e.description,
    }
    return jsonify(context), HTTPStatus.UNPROCESSABLE_ENTITY


# 5xx
def internal_server_error(e: exc.InternalServerError) -> Tuple[Response, int]:
    context = {
        'status': ResponseStatuses.failed.value,
        'message': 'Something went wrong...',
        'details': e.description,
    }
    return jsonify(context), HTTPStatus.INTERNAL_SERVER_ERROR
