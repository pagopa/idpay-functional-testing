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
    res = accept_terms_and_condition(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.path}', token,
        secrets.initiatives.cashback_like.id)
    assert res.status_code == 204
    res = check_prerequisites(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.initiative}', token,
        secrets.initiatives.cashback_like.id)
    assert res.status_code == 200
    res = pdnd_autocertification(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.consent}', token,
        secrets.initiatives.cashback_like.id)
    assert res.status_code == 202
    res = status_onboarding(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.path}/{secrets.initiatives.cashback_like.id}{settings.IDPAY.endpoints.onboarding.status}',
        token,
        secrets.initiatives.cashback_like.id)
    assert res.status_code == 200
    assert res.json()['status'] in ('ONBOARDING_OK', 'ON_EVALUATION')
