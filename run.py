# -*- coding: utf-8 -*-
"""It is a pet project in Flask to get some experience on developing a JWT auth REST-API.

__author__ = "Volodymyr Miroshnychenko"
__credits__ = ["Volodymyr Miroshnychenko"]
__version__ = "0.5.0"
__maintainer__ = "Volodymyr Miroshnychenko"
__email__ = "miroshveva98@gmail.com"
__status__ = "Development"
"""

import src.utils as utils
from src.app import create_app

# init API app
auth_api = create_app()

# init utils
# JWT utils
access_token_generator = utils.AccessTokenGenerator(auth_api.config)
refresh_token_generator = utils.RefreshTokenGenerator(auth_api.config)
jwt_decoder = utils.JWTDecoder(auth_api.config)
refresh_token_storage_controller = utils.RefreshTokenStorageController(
    auth_api.config['REDIS_HOST'],
    auth_api.config['REDIS_PORT'],
    auth_api.config['REDIS_JWT_DB'],
)
# reset PWD utils
reset_password_token_generator = utils.ResetPasswordTokenGenerator(auth_api.config)
reset_password_token_decoder = utils.ResetPasswordTokenDecoder(auth_api.config)
# email utils
email_sender = utils.EmailSender(auth_api.config, auth_api.flask_app)

# get Migrate
migrate = auth_api.migrate

# OAuth
oauth = auth_api.oauth
google_util_config = utils.create_google_config(
    auth_api.config['BASE_DIR'],
    auth_api.config['GOOGLE_CONFIG_FILENAME'],
)
google_login_util = utils.GoogleLoginUtil(google_util_config)

# get Flask app for actual run
app = auth_api.flask_app
