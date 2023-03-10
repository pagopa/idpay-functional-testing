"""Endpoint tests
"""
import pytest

from api.token_io import introspect, login
from conf.configuration import settings
from util import faker_wrapper


@pytest.mark.IO
def test_login_io():
    """IO login is emulated by a stub which allows to get a token from a tax code
    and then introspect the token
    """

    test_fc = faker_wrapper.fake_fc()

    res = login(f'{settings.base_path.IO}{settings.BPD.domain}{settings.BPD.endpoints.login}', test_fc)
    token = res.content.decode('utf-8')
    res = introspect(f'{settings.base_path.IO}{settings.BPD.domain}{settings.BPD.endpoints.user}', token)

    assert res.json()['fiscal_code'] == test_fc
