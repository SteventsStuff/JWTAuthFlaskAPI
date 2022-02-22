import typing as t
from http import HTTPStatus

from flask import Flask
from flask_migrate import Migrate
from flask_log_request_id import RequestID
from authlib.integrations.flask_client import OAuth

import log
from src.models import db
from src.schemas import ma
from src.exceptions import AppIsNotConfigured
from src.views.auth import auth_bp
from src.views.social_auth import social_auth_bp
from src.views.users import users_bp
from src.views import errors as err
from config import APIConfig

logger = log.APILogger(__name__)


class App:
    _APP_NOT_CONFIGURED_MSG: str = 'Can not get {} property. Your app is not configured! ' \
                                   'You must call "configure_app" method first!'

    def __init__(self) -> None:
        self._app: Flask = Flask(__name__)
        self._is_configured: bool = False
        self._migrate: Migrate = Migrate(self._app)
        self._oauth: OAuth = OAuth(self._app)

        RequestID(self._app)

    def configure_app(self, config: t.Type[APIConfig]) -> None:
        logger.info('Configuring application...')
        self._app.config.from_object(config)

        self._init_db()
        self._init_marshmallow()

        self._register_blueprints()
        self._register_error_handlers()

        self._is_configured = True

    @property
    def config(self) -> t.Dict[t.Any, t.Any]:
        if not self._is_configured:
            msg = self._APP_NOT_CONFIGURED_MSG.format('config')
            logger.error(msg)
            raise AppIsNotConfigured(msg)
        return self._app.config

    @property
    def flask_app(self) -> Flask:
        if not self._is_configured:
            msg = self._APP_NOT_CONFIGURED_MSG.format('flask_app')
            logger.error(msg)
            raise AppIsNotConfigured(msg)
        return self._app

    @property
    def migrate(self) -> Migrate:
        if not self._is_configured:
            msg = self._APP_NOT_CONFIGURED_MSG.format('migrate')
            logger.error(msg)
            raise AppIsNotConfigured(msg)
        return self._migrate

    @property
    def oauth(self) -> OAuth:
        if not self._is_configured:
            msg = self._APP_NOT_CONFIGURED_MSG.format('oauth')
            logger.error(msg)
            raise AppIsNotConfigured(msg)
        return self._oauth

    def _init_db(self) -> None:
        from src.models import User
        db.init_app(self._app)
        db.create_all(app=self._app)

    def _init_marshmallow(self) -> None:
        ma.init_app(self._app)

    def _register_blueprints(self) -> None:
        self._app.register_blueprint(auth_bp)
        self._app.register_blueprint(social_auth_bp)
        self._app.register_blueprint(users_bp)

    def _register_error_handlers(self) -> None:
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
