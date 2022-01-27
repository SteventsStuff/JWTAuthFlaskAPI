import typing as t

import log
from flask import Flask
from flask_mail import Mail, Message

logger = log.APILogger(__name__)


class EmailSender:
    def __init__(self, config: t.Dict[t.Any, t.Any], flask_app: Flask) -> None:
        self._app_config: t.Dict[t.Any, t.Any] = config
        self._mail: Mail = Mail(flask_app)

    def send_password_reset_email(self, email_address: str, token: str) -> None:
        body = f'Please, use that token to reset your password: {token}'
        name = self._app_config['SERVER_NAME'].split(':')[0]
        sender = (name, 'noreply@authapi.com')
        context = {
            'subject': 'Password Reset',
            'recipients': [email_address],
            'body': body,
            'sender': sender,
        }

        logger.info(f'Sending email to with password recovery information to {email_address}...')
        message = Message(**context)
        try:
            self._mail.send(message)
        # todo: bad exception handling
        except Exception as e:
            logger.error(f'Failed to send an email to {email_address}.\nError: {e}')
