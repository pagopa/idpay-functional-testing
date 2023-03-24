"""Tests on a not yet started initiative
"""
import pytest

from api.issuer import enroll
from conf.configuration import secrets
from util import dataset_utility
from util.certs_loader import load_pm_public_key
from util.encrypt_utilities import pgp_string_routine


@pytest.mark.enroll
def test_fail_onboarding_issuer_citizen_not_onboard():
    """Issuer enroll of a non-onboard citizen. The expected result is a 404 obtained from IDPay.
    This is due to the missing onboard of a citizen.
    """
    test_fc = dataset_utility.fake_fc()
    test_pan = dataset_utility.fake_pan()

    res = enroll(secrets.initiatives.not_started.id,
                 test_fc,
                 {
                     "brand": "VISA",
                     "type": "DEB",
                     "pgpPan": pgp_string_routine(test_pan, load_pm_public_key()).decode('unicode_escape'),
                     "expireMonth": "08",
                     "expireYear": "2023",
                     "issuerAbiCode": "03069",
                     "holder": "TEST"
                 }
                 )
    assert res.status_code == 404


@pytest.mark.enroll
def test_fail_onboarding_issuer_malformed_pgp():
    """Issuer enroll of a non-onboard citizen. The expected result is a 404 obtained from IDPay.
    This is due to the missing onboard of a citizen.
    """
    test_fc = dataset_utility.fake_fc()
    test_pan = dataset_utility.fake_pan()

    res = enroll(secrets.initiatives.not_started.id,
                 test_fc, {
                     "brand": "VISA",
                     "type": "DEB",
                     "pgpPan": '0' + pgp_string_routine(test_pan, load_pm_public_key()).decode('unicode_escape'),
                     "expireMonth": "08",
                     "expireYear": "2023",
                     "issuerAbiCode": "03069",
                     "holder": "TEST"
                 })

    assert res.status_code == 500
