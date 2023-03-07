"""Tests on a not yet started initiative
"""
import pytest

from api.enrollment_issuer import enroll
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

    res = login("https://api-io.uat.cstar.pagopa.it/bpd/pagopa/api/v1/login", my_fiscal_code)
    token = res.content.decode('utf-8')
    res = acceptTandC("https://api-io.uat.cstar.pagopa.it/idpay/onboarding/", token, secrets.initiatives.not_started.id)

    assert res.json()['code'] == 403
    assert res.json()['message'] == 'The initiative has not yet begun'
    assert res.json()['details'] == 'INITIATIVE_NOT_STARTED'


@pytest.mark.IO
def test_fail_onboarding_wrong_token():
    """IO login is emulated by a stub which allows to get a token from a tax code
    and then introspect the token
    """
    test_fc = faker_wrapper.fake_fc()

    res = login("https://api-io.uat.cstar.pagopa.it/bpd/pagopa/api/v1/login", my_fiscal_code)
    token = res.content.decode('utf-8')
    res = acceptTandC("https://api-io.uat.cstar.pagopa.it/idpay/onboarding/", token + '0',
                      secrets.initiatives.not_started.id)
    assert res.status_code == 401
