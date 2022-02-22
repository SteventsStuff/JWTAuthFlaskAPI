import json
import typing as t
from pathlib import Path

from requests import Response

import run


class GoogleLoginUnit:
    def __init__(self, config: t.Dict[str, t.Any]) -> None:
        self._google = run.oauth.register(**config)

    def authorize_redirect(self, url: str):
        return self._google.authorize_redirect(url)

    def authorize_access_token(self) -> str:
        return self._google.authorize_access_token()

    def get(self, *args, **kwargs) -> Response:
        return self._google.get(*args, **kwargs)


def get_config_from_json(base_dir: Path, filename: str) -> t.Dict[str, t.Any]:
    file_path = base_dir / filename
    with open(file_path) as f:
        return json.load(f)


def create_google_config(base_dir: Path, filename: str) -> t.Dict[str, t.Any]:
    google_auth_config = get_config_from_json(base_dir, filename)
    google_auth_config.update({
        'client_id': run.auth_api.config['GOOGLE_CLIENT_ID'],
        'client_secret': run.auth_api.config['GOOGLE_CLIENT_SECRET'],
    })
    return google_auth_config
