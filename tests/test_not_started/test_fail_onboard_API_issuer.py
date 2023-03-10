"""Tests on a not yet started initiative
"""
import pytest

from api.enrollment_issuer import enroll
from conf.configuration import secrets, settings
from util import faker_wrapper


@pytest.mark.enroll
def test_fail_onboarding_issuer_citizen_not_onboard():
    """Issuer enroll of a non-onboard citizen. The expected result is a 404 obtained from IDPay.
    This is due to the missing onboard of a citizen.
    """
    test_fc = faker_wrapper.fake_fc()

    res = enroll(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.enrollment.start_path}/{secrets.initiatives.not_started.id}{settings.IDPAY.endpoints.enrollment.end_path}',
        test_fc, {
            "brand": "VISA",
            "type": "DEB",
            "pgpPan": secrets.initiatives.not_started.pgpan,
            "expireMonth": "08",
            "expireYear": "2023",
            "issuerAbiCode": "03069",
            "holder": "TEST"
        })
    assert res.status_code == 404


@pytest.mark.enroll
def test_fail_onboarding_issuer_malformed_pgp():
    """Issuer enroll of a non-onboard citizen. The expected result is a 404 obtained from IDPay.
    This is due to the missing onboard of a citizen.
    """
    test_fc = faker_wrapper.fake_fc()

    res = enroll(
        f'{settings.base_path.CSTAR}{settings.IDPAY.domain}{settings.IDPAY.endpoints.enrollment.start_path}/{secrets.initiatives.not_started.id}{settings.IDPAY.endpoints.enrollment.end_path}',
        test_fc, {
            "brand": "VISA",
            "type": "DEB",
            "pgpPan": "0" + secrets.initiatives.not_started.pgpan,
            "expireMonth": "08",
            "expireYear": "2023",
            "issuerAbiCode": "03069",
            "holder": "TEST"
        })

    assert res.status_code == 500
