"""Endpoint tests
"""
import pytest

from api.token_io import introspect
from api.token_io import login
from util import dataset_utility


@pytest.mark.IO
def test_login_io():
    """IO login is emulated by a stub which allows to get a token from a tax code
    and then introspect the token
    """

    test_fc = dataset_utility.fake_fc()

    res = login(test_fc)
    token = res.content.decode('utf-8')
    res = introspect(token)

    assert res.json()['fiscal_code'] == test_fc
