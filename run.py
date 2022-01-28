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
    host=auth_api.config['R_HOST'],
    port=auth_api.config['R_PORT'],
    db=auth_api.config['R_JWT_DB'],
)
# reset PWD utils
reset_password_token_generator = utils.ResetPasswordTokenGenerator(auth_api.config)
reset_password_token_decoder = utils.ResetPasswordTokenDecoder(auth_api.config)
# email utils
email_sender = utils.EmailSender(auth_api.config, auth_api.flask_app)

# get Migrate
migrate = auth_api.migrate

# get Flask app for actual run
app = auth_api.flask_app
