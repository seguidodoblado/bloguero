from __future__ import annotations

import json
from pathlib import Path

import keyring
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from bloguero.i18n import _

SCOPES = ["https://www.googleapis.com/auth/blogger"]

_KEYRING_SERVICE = "bloguero"
_KEYRING_USERNAME = "refresh_token"

CONFIG_DIR = Path.home() / ".config" / "bloguero"
CLIENT_SECRET_PATH = CONFIG_DIR / "client_secret.json"


class AuthError(Exception):
    """El flujo de autenticación falló o no hay credenciales válidas."""


def has_stored_credentials() -> bool:
    return keyring.get_password(_KEYRING_SERVICE, _KEYRING_USERNAME) is not None


def get_credentials() -> Credentials:
    """Devuelve credenciales válidas, renovando o pidiendo login si hace falta."""
    refresh_token = keyring.get_password(_KEYRING_SERVICE, _KEYRING_USERNAME)
    if refresh_token:
        creds = _credentials_from_refresh_token(refresh_token)
        try:
            creds.refresh(Request())
        except RefreshError as exc:
            clear_stored_credentials()
            raise AuthError(_("El token guardado ya no es válido, inicia sesión de nuevo")) from exc
        return creds

    return _run_oauth_flow()


def clear_stored_credentials() -> None:
    try:
        keyring.delete_password(_KEYRING_SERVICE, _KEYRING_USERNAME)
    except keyring.errors.PasswordDeleteError:
        pass


def _run_oauth_flow() -> Credentials:
    if not CLIENT_SECRET_PATH.exists():
        raise AuthError(
            _("Falta el cliente OAuth de escritorio en {path}. Descárgalo desde Google Cloud Console.").format(
                path=CLIENT_SECRET_PATH
            )
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    creds = flow.run_local_server(port=0)

    if creds.refresh_token:
        keyring.set_password(_KEYRING_SERVICE, _KEYRING_USERNAME, creds.refresh_token)

    return creds


def _credentials_from_refresh_token(refresh_token: str) -> Credentials:
    client_config = json.loads(CLIENT_SECRET_PATH.read_text())["installed"]
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=client_config["token_uri"],
        client_id=client_config["client_id"],
        client_secret=client_config["client_secret"],
        scopes=SCOPES,
    )
