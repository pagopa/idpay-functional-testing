"""Card enrollment tests
"""
import pytest

from api.issuer import enroll
from conf.configuration import secrets
from util.certs_loader import load_pm_public_key
from util.dataset_utility import fake_fc, fake_pan
from util.encrypt_utilities import pgp_string_routine
from util.utility import card_enroll, onboard_io


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.2')
def test_enrollment_api_issuer():
    """Card enrollment process through Issuer API
    """
    test_fc = fake_fc()
    pan = fake_pan()

    assert onboard_io(test_fc, secrets.initiatives.cashback_like.id).json()['status'] == 'ONBOARDING_OK'
    assert any(operation['operationType'] == 'ADD_INSTRUMENT' for operation in
               card_enroll(test_fc, pan, secrets.initiatives.cashback_like.id).json()['operationList'])


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.2')
def test_fail_enrollment_issuer_not_onboard():
    """Card enrollment process through Issuer API
    """
    test_fc = fake_fc()
    pan = fake_pan()
    res = enroll(secrets.initiatives.cashback_like.id,
                 test_fc,
                 {
                     'brand': 'VISA',
                     'type': 'DEB',
                     'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     'expireMonth': '08',
                     'expireYear': '2023',
                     'issuerAbiCode': '03069',
                     'holder': 'TEST'
                 }
                 )
    assert res.status_code == 404
