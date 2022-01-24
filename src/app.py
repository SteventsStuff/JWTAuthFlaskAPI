import typing as t
from http import HTTPStatus

from flask import Flask

from src.models import db
from src.schemas import ma
from src.exceptions import AppIsNotConfigured
from src.views.auth import auth_bp
from src.views.users import users_bp
from src.views import errors as err
from config import APIConfig


class App:
    def __init__(self) -> None:
        self._app: Flask = Flask(__name__)
        self._is_configured: bool = False

    def configure_app(self, config: t.Type[APIConfig]) -> None:
        self._app.config.from_object(config)

        from src.models import User
        self._init_db()
        self._init_marshmallow()
        self._register_blueprints()
        self._register_error_handlers()

        self._is_configured = True

    @property
    def config(self) -> t.Dict[t.Any, t.Any]:
        if not self._is_configured:
            raise AppIsNotConfigured('Your app is not configured! '
                                     'You must call "configure_app" method first!')
        return self._app.config

    @property
    def flask_app(self) -> Flask:
        if not self._is_configured:
            raise AppIsNotConfigured('Your app is not configured! '
                                     'You must call "configure_app" method first!')
        return self._app

    def _init_db(self) -> None:
        db.init_app(self._app)
        db.create_all(app=self._app)

    def _init_marshmallow(self) -> None:
        ma.init_app(self._app)

    def _register_blueprints(self) -> None:
        self._app.register_blueprint(auth_bp)
        self._app.register_blueprint(users_bp)

    def _register_error_handlers(self) -> None:
        # todo: review later
        # 4xx
        self._app.register_error_handler(HTTPStatus.BAD_REQUEST, err.bad_request)
        self._app.register_error_handler(HTTPStatus.UNAUTHORIZED, err.unauthorized)
        self._app.register_error_handler(HTTPStatus.NOT_FOUND, err.page_not_found)
        self._app.register_error_handler(HTTPStatus.METHOD_NOT_ALLOWED, err.method_not_allowed)
        self._app.register_error_handler(HTTPStatus.CONFLICT, err.conflict)
        self._app.register_error_handler(HTTPStatus.UNPROCESSABLE_ENTITY, err.unprocessed_entity)
        # 5xx
        self._app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR, err.internal_server_error)


def create_app() -> App:
    application = App()
    application.configure_app(APIConfig)
    return application
