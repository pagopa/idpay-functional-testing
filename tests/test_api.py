"""Endpoint tests
"""
import pytest

from api.endpoints import get_uuid, get_headers
from conf.configuration import settings, secrets


@pytest.mark.API
def test_get_uuid():
    """Test uuid endpoint
    """
    response = get_uuid()
    assert len(response.json()['uuid']) == 36, "value was odd, should be even"
    assert response.status_code == 200


@pytest.mark.API
def test_get_headers():
    """Test mirror headers endpoint
    """
    response = get_headers(secrets.api_key)
    assert secrets.api_key == response.json()['headers'][settings.API_KEY_HEADER]
