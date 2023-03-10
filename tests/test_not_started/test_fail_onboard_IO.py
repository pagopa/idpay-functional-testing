"""Tests on a not yet started initiative
"""
import pytest

from api.onboarding_io import accept_terms_and_condition
from api.token_io import login
from conf.configuration import secrets, settings
from util import faker_wrapper


@pytest.mark.IO
def test_fail_onboarding():
    """IO login is emulated by a stub which allows to get a token from a tax code
    and then introspect the token
    """
    test_fc = faker_wrapper.fake_fc()

    res = login(f'{settings.base_path.IO}{settings.BPD.domain}{settings.BPD.endpoints.login}', test_fc)
    token = res.content.decode('utf-8')
    res = accept_terms_and_condition(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding}', token,
        secrets.initiatives.not_started.id)

    assert res.json()['code'] == 403
    assert res.json()['message'] == settings.initiatives.not_started.message
    assert res.json()['details'] == settings.initiatives.not_started.details


@pytest.mark.IO
def test_fail_onboarding_wrong_token():
    """IO login is emulated by a stub which allows to get a token from a tax code
    and then introspect the token
    """
    test_fc = faker_wrapper.fake_fc()
    res = login(f'{settings.base_path.IO}{settings.BPD.domain}{settings.BPD.endpoints.login}', test_fc)
    token = res.content.decode('utf-8')
    res = accept_terms_and_condition(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding}', token + '0',
        secrets.initiatives.not_started.id)
    assert res.status_code == 401
