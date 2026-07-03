"""Tests on a not yet started initiative
"""
import pytest

from api.onboarding_io import save_onboarding
from api.token_io import login
from conf.configuration import secrets
from util import dataset_utility


@pytest.mark.IO
def test_fail_onboarding():
    """IO login is emulated by a stub which allows to get a token from a tax code
    and then introspect the token
    """
    test_fc = dataset_utility.fake_fc()

    res = login(test_fc)
    token = res.content.decode('utf-8')
    res = save_onboarding(token, secrets.initiatives.not_started.id)

    assert res.status_code == 403
    assert res.json()['code'] == 'ONBOARDING_INITIATIVE_NOT_STARTED'


@pytest.mark.IO
def test_fail_onboarding_wrong_token():
    """IO login is emulated by a stub which allows to get a token from a tax code
    and then introspect the token
    """
    test_fc = dataset_utility.fake_fc()
    res = login(test_fc)
    token = res.content.decode('utf-8')
    res = save_onboarding(token + '0', secrets.initiatives.not_started.id)
    assert res.status_code == 401
