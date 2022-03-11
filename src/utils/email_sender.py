import typing as t

from flask import Flask
from flask_mail import Mail, Message

import log
import run

logger = log.APILogger(__name__)


class EmailSender:
    def __init__(self, config: t.Dict[t.Any, t.Any], flask_app: Flask) -> None:
        self._app_config: t.Dict[t.Any, t.Any] = config
        self._mail: Mail = Mail(flask_app)

    def send_password_reset_email(self, email_address: str, token: str) -> None:
        """Sends an email with a reset token to a receiver.

        Args:
            email_address (str): Receiver email address
            token (str): Password reset token
        """

        context = self._create_email_context(email_address, token)
        logger.info(f'Sending am email to with password recovery information to {email_address}...')
        message = Message(**context)

        if run.app.config['DEBUG'] == 1:
            print(message)
            logger.debug(
                f'Sending a fake email to with password recovery information to {email_address}...\nMessage: {message}'
            )
            return

        try:
            self._mail.send(message)
        except Exception as e:
            logger.error(f'Failed to send an email to {email_address}.\nError: {e}')

    def _create_email_context(self, email_address: str, token: str) -> t.Dict[str, t.Any]:
        body = f'Please, use that token to reset your password: {token}'
        name = self._app_config['SERVER_NAME'].split(':')[0]
        sender = (name, 'noreply@authapi.com')

        context = {
            'subject': 'Password Reset',
            'recipients': [email_address],
            'body': body,
            'sender': sender,
        }
        return context
