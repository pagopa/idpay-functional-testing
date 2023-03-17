"""IBAN enrollment test
"""
import pytest

from api.issuer import enroll
from conf.configuration import secrets
from util import dataset_utility
from util.certs_loader import load_pm_public_key
from util.encrypt_utilities import pgp_string_routine
from util.utility import onboard_io, get_io_token, iban_enroll


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.3')
def test_enrollment_iban():
    """IBAN enrollment process through IO API
    """
    test_fc = dataset_utility.fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')

    # Onboard IO
    assert onboard_io(test_fc).json()['status'] == 'ONBOARDING_OK'

    token = get_io_token(test_fc)

    assert any(
        operation['operationType'] == 'ADD_IBAN' for operation in iban_enroll(token, curr_iban).json()['operationList'])


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.3')
def test_fail_enrollment_issuer_not_onboard():
    """IBAN enrollment process through IO API
    """

    test_fc = dataset_utility.fake_fc()

    res = enroll(secrets.initiatives.cashback_like.id,
                 test_fc, {
                     "brand": "VISA",
                     "type": "DEB",
                     "pgpPan": pgp_string_routine('0000000000000000', load_pm_public_key()).decode('unicode_escape'),
                     "expireMonth": "08",
                     "expireYear": "2023",
                     "issuerAbiCode": "03069",
                     "holder": "TEST"
                 })

    assert res.status_code == 404
