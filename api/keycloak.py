"""Keycloak authentication endpoints."""
import requests

from conf.configuration import settings


def get_client_credentials_token(token_url, client_id, client_secret, scope=None):
    """Obtain an access token with the OAuth 2.0 client-credentials grant."""
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    if scope:
        data['scope'] = scope

    return requests.post(
        token_url,
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=settings.default_timeout,
    )
