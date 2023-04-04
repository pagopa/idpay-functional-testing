"""IBAN enrollment test
"""
import pytest

from api.idpay import enroll_iban
from api.idpay import wallet
from conf.configuration import secrets
from conf.configuration import settings
from util import dataset_utility
from util.utility import get_io_token
from util.utility import iban_enroll
from util.utility import onboard_io
from util.utility import retry_wallet

initiative_id = secrets.initiatives.cashback_like.id

only_iban_status = settings.IDPAY.endpoints.wallet.statuses.not_refundable_only_iban


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.use_case('1.3')
def test_enrollment_iban():
    """IBAN enrollment process through IO API
    """
    test_fc = dataset_utility.fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    token = get_io_token(test_fc)

    onboard_io(test_fc, initiative_id).json()

    iban_enroll(test_fc, curr_iban, secrets.initiatives.cashback_like.id)

    retry_wallet(expected=only_iban_status, request=wallet, token=token,
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
