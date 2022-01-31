import os
import types as t

from dotenv import dotenv_values

basedir = os.path.abspath(os.path.dirname(__file__))

env = t.MappingProxyType({
    **dotenv_values('.env.flask'),
    **dotenv_values('.env.secret'),
    **dotenv_values('.env.shared'),
})


class APIConfig:
    # KEY
    SECRET_KEY = env.get('SECRET_KEY', 'top-secret!')

    # SERVER
    SERVER_NAME = env.get('SERVER_NAME', '127.0.0.1:5000')
    DEBUG = env.get('DEBUG', 'true')
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
    R_HOST = env.get('R_HOST', '127.0.0.1')
    R_PORT = int(env.get('R_PORT', '6379'))
    R_PWD = env.get('R_PWD', '')
    R_JWT_DB = int(env.get('R_JWT_DB', 0))
    R_RESET_EMAIL_TOKENS_DB = int(env.get('R_RESET_EMAIL_TOKENS_DB', 1))

    # EMAIL
    MAIL_EXPIRES_IN = int(env.get('MAIL_EXPIRES_IN', 120))
    MAIL_SERVER = env.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = env.get('MAIL_PORT', 25)
    MAIL_USE_TLS = bool(env.get('MAIL_USE_TLS', False))
    # MAIL_USE_SSL = bool(env.get('MAIL_USE_SSL', False))
    MAIL_DEBUG = int(env.get('MAIL_DEBUG', 1))
    MAIL_USERNAME = env.get('MAIL_USERNAME', None)
    MAIL_PASSWORD = env.get('MAIL_PASSWORD', None)
    # MAIL_DEFAULT_SENDER = env.get('MAIL_DEFAULT_SENDER', 'noreply@authapi.com')
    MAIL_MAX_EMAILS = env.get('MAIL_MAX_EMAILS', 1)
    # MAIL_SUPPRESS_SEND = env.get('MAIL_SUPPRESS_SEND', 'testing')
    # MAIL_ASCII_ATTACHMENTS = env.get('MAIL_ASCII_ATTACHMENTS', False)
