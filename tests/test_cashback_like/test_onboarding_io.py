"""Onboard tests
"""
import pytest

from api.onboarding_io import accept_terms_and_condition, check_prerequisites, pdnd_autocertification, status_onboarding
from api.token_io import introspect, login
from conf.configuration import settings, secrets
from util import dataset_utility


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.1')
def test_onboard_io():
    """Onboarding process through IO
    """

    test_fc = dataset_utility.fake_fc()

    res = login(test_fc)
    token = res.content.decode('utf-8')
    res = introspect(token)
    assert res.json()['fiscal_code'] == test_fc
    res = accept_terms_and_condition(token, secrets.initiatives.cashback_like.id)
    assert res.status_code == 204
    res = check_prerequisites(
        token,
        secrets.initiatives.cashback_like.id)
    assert res.status_code == 200
    res = pdnd_autocertification(
        token,
        secrets.initiatives.cashback_like.id)
    assert res.status_code == 202
    res = status_onboarding(
        token,
        secrets.initiatives.cashback_like.id)
    assert res.status_code == 200
    assert res.json()['status'] in ('ONBOARDING_OK', 'ON_EVALUATION')
