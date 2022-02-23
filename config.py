import os
import types as t
from pathlib import Path

from dotenv import dotenv_values

basedir = os.path.abspath(os.path.dirname(__file__))

env = t.MappingProxyType({
    **dotenv_values('.env.flask'),
    **dotenv_values('.env.secret'),
    **dotenv_values('.env.shared'),
})


class APIConfig:
    """A class for the Flask application"""

    BASE_DIR = Path()

    # KEY
    SECRET_KEY = env.get('SECRET_KEY', 'top-secret!')

    # SERVER
    SERVER_NAME = env.get('SERVER_NAME', '127.0.0.1:5000')
    DEBUG = bool(int(env.get('DEBUG', '1')))
    ENV = env.get('FLASK_ENV', 'development')
    # https://flask.palletsprojects.com/en/2.0.x/config/#configuring-from-data-files "JSON_SORT_KEYS"
    JSON_SORT_KEYS = bool(env.get('JSON_SORT_KEYS', 1))

    # DB
    SQLALCHEMY_DATABASE_URI = env.get('DATABASE_URL', '').format(
        DB_USERNAME=env.get('DB_USERNAME', ''),
        DB_PWD=env.get('DB_PWD', ''),
        DB_NAME=env.get('DB_NAME', ''),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = bool(env.get('SQLALCHEMY_TRACK_MODIFICATIONS', 0))

    # JWT TOKEN
    JWT_ACCESS_TOKEN_EXPIRATION = int(env.get('JWT_ACCESS_TOKEN_EXPIRATION', 30))
    JWT_REFRESH_TOKEN_EXPIRATION = int(env.get('JWT_REFRESH_TOKEN_EXPIRATION', 30))
    JWT_ALGORITHM = env.get('JWT_ALGORITHM', 'HS256')
    JWT_ISSUER = env.get('JWT_ISSUER')

    # REDIS
    REDIS_HOST = env.get('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = int(env.get('REDIS_PORT', '6379'))
    REDIS_PWD = env.get('REDIS_PWD', '')
    REDIS_JWT_DB = int(env.get('REDIS_JWT_DB', 0))
    REDIS_RESET_EMAIL_TOKENS_DB = int(env.get('REDIS_RESET_EMAIL_TOKENS_DB', 1))

    # EMAIL
    MAIL_EXPIRES_IN = int(env.get('MAIL_EXPIRES_IN', 120))
    MAIL_SERVER = env.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = env.get('MAIL_PORT', 25)
    MAIL_USE_TLS = bool(env.get('MAIL_USE_TLS', False))
    MAIL_DEBUG = int(env.get('MAIL_DEBUG', 1))
    MAIL_USERNAME = env.get('MAIL_USERNAME', None)
    MAIL_PASSWORD = env.get('MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = env.get('MAIL_DEFAULT_SENDER', 'noreply@authapi.com')
    MAIL_MAX_EMAILS = env.get('MAIL_MAX_EMAILS', 1)

    # GOOGLE AUTH
    GOOGLE_CLIENT_ID = env.get('GOOGLE_CLIENT_ID', 'no-id')
    GOOGLE_CLIENT_SECRET = env.get('GOOGLE_CLIENT_SECRET', 'no-secret')
    GOOGLE_CONFIG_FILENAME = env.get('GOOGLE_CONFIG_FILENAME', 'googleConfig.json')
