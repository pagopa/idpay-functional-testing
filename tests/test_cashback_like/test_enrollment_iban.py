"""IBAN enrollment test
"""
import pytest

from conf.configuration import secrets
from idpay import wallet, enroll_iban
from util import dataset_utility
from util.utility import onboard_io, get_io_token, iban_enroll, retry_wallet

initiative_id = secrets.initiatives.cashback_like.id


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.3')
def test_enrollment_iban():
    """IBAN enrollment process through IO API
    """
    test_fc = dataset_utility.fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')

    # Onboard IO
    assert onboard_io(test_fc, initiative_id).json()['status'] == 'ONBOARDING_OK'

    token = get_io_token(test_fc)

    iban_enroll(token, curr_iban, secrets.initiatives.cashback_like.id)

    retry_wallet(expected='NOT_REFUNDABLE_ONLY_IBAN', request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='IBAN not registered')


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.3')
def test_fail_enrollment_iban_citizen_not_onboard():
    """Fail IBAN enrollment process through IO API, citizen not onboard
    """

    test_fc = dataset_utility.fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')

    token = get_io_token(test_fc)
    res = enroll_iban(initiative_id,
                      token,
                      {
                          'iban': curr_iban,
                          'description': 'TEST Bank account'
                      }
                      )
    assert res.status_code == 404

    res = wallet(initiative_id, token)
    assert res.status_code == 404
