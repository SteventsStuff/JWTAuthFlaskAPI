import typing as t
import uuid

from src.abstractions.abc_mapper import ABCMapper


class GoogleProfileMapper(ABCMapper):
    def __init__(self, user_info: t.Dict[str, t.Union[str, bool]]) -> None:
        self._user_info: t.Dict[str, t.Union[str, bool]] = user_info

    def create_payload(self) -> t.Dict[str, t.Any]:
        """
        user_info = {
            email: "example@gmail.com",
            family_name: "SecondName",
            given_name: "FirstName",
            id: "777777777777788877777",
            locale: "en",
            name: "FirstName SecondName",
            picture: "https://lh3.googleusercontent.com/a-/path-to-pic-foo-bar",
            verified_email: true
        }
        Returns:

        """
        payload = {
            'username': self._user_info['email'].split('@')[0][:50],
            'email_address': self._user_info['email'],
            'password_hash': str(uuid.uuid4()),
            'first_name': self._user_info['family_name'],
            'last_name': self._user_info['given_name'],
        }
        return payload
