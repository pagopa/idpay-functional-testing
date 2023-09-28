"""Onboard tests
"""
import json
import math
import random
import string

import pytest

from api.idpay import get_initiative_statistics
from api.idpay import timeline
from api.idpay import wallet
from api.onboarding_io import accept_terms_and_conditions
from api.onboarding_io import pdnd_autocertification
from api.token_io import introspect
from api.token_io import login
from conf.configuration import secrets
from conf.configuration import settings
from util.dataset_utility import fake_fc
from util.dataset_utility import fake_temporary_fc
from util.dataset_utility import get_random_unicode
from util.utility import check_statistics
from util.utility import get_io_token
from util.utility import onboard_io

initiative_id = secrets.initiatives.cashback_like.id
wallet_statuses = settings.IDPAY.endpoints.wallet.statuses


@pytest.mark.IO
@pytest.mark.onboard
def test_onboard_io():
    """Onboarding process through IO
    """
    test_fc = fake_fc()
    onboard_io(test_fc, initiative_id).json()


@pytest.mark.IO
@pytest.mark.onboard
def test_onboard_io_temporary_fc():
    """Onboarding process through IO with a temporary fiscal code
    """
    test_fc = fake_temporary_fc()
    onboard_io(test_fc, initiative_id).json()


@pytest.mark.IO
@pytest.mark.onboard
def test_onboard_blank_fc():
    """Onboarding process through IO of a blank test Fiscal Code
    """
    test_fc = ''
    token = get_io_token(test_fc)
    assert json.loads(token)['returnMessages']['ERROR'][0]['severity'] == 'ERROR'
    assert json.loads(token)['returnMessages']['ERROR'][0]['message'] == 'Il campo fiscalcode è obbligatorio'


@pytest.mark.IO
@pytest.mark.onboard
def test_onboard_space_fc():
    """Onboarding process through IO of a blank test Fiscal Code
    """
    test_fc = '  '
    token = get_io_token(test_fc)
    assert json.loads(token)['returnMessages']['ERROR'][0]['severity'] == 'ERROR'
    assert json.loads(token)['returnMessages']['ERROR'][0]['message'] == 'Il campo fiscalcode è obbligatorio'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.need_fix
def test_onboard_unicode():
    """Onboarding process through IO of a test Fiscal Code made of random Unicode characters
    """
    test_fc = get_random_unicode(random.randint(0, 100))
    token = get_io_token(test_fc)

    res = introspect(token)
    assert res.json()['fiscal_code'] == test_fc

    res = accept_terms_and_conditions(token, initiative_id)
    assert res.status_code == 400
    assert res.json()['code'] == 'FISCAL_CODE_NOT_VALID'
    assert res.json()['message'] == settings.IDPAY.endpoints.onboarding.enrollment.invalid_fc_message

    res = wallet(initiative_id=initiative_id, token=token)
    assert res.status_code == 400
    assert res.json()['code'] == 'FISCAL_CODE_NOT_VALID'
    assert res.json()['message'] == settings.IDPAY.endpoints.onboarding.enrollment.invalid_fc_message


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.need_fix
def test_onboard_long_fc():
    """Onboarding process through IO of a test Fiscal Code longer than normal
    """
    test_fc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=int((math.pow(2, 10)))))
    token = get_io_token(test_fc)

    res = introspect(token)
    assert res.json()['fiscal_code'] == test_fc

    res = accept_terms_and_conditions(token, initiative_id)
    assert res.status_code == 400
    assert res.json()['code'] == 'FISCAL_CODE_NOT_VALID'
    assert res.json()['message'] == settings.IDPAY.endpoints.onboarding.enrollment.invalid_fc_message

    res = wallet(initiative_id=initiative_id, token=token)
    assert res.status_code == 400
    assert res.json()['code'] == 'FISCAL_CODE_NOT_VALID'
    assert res.json()['message'] == settings.IDPAY.endpoints.onboarding.enrollment.invalid_fc_message


@pytest.mark.IO
@pytest.mark.onboard
def test_onboard_too_long_fc():
    """Onboarding process through IO of a test Fiscal Code longer than maximum length of the URL
    """
    test_fc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=int((math.pow(2, 13)))))
    res = login(test_fc)
    assert res.status_code == 414


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.need_fix
def test_timeline_without_ever_onboard():
    """The timeline and wallet of an ever onboarded citizen are not found
    """
    test_fc = fake_fc()
    token_io = get_io_token(test_fc)

    res = wallet(initiative_id=initiative_id, token=token_io)
    assert res.status_code == 404
    res = timeline(initiative_id=initiative_id, token=token_io)
    assert res.status_code == 404


@pytest.mark.IO
@pytest.mark.onboard
def test_onboard_two_times():
    """Repeat the onboarding of the same citizen and check if the counters change
    """
    organization_id = secrets.organization_id
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    test_fc = fake_temporary_fc()

    onboard_io(test_fc, initiative_id).json()
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=0,
                     rewarded_trxs_increment=0, skip_trx_check=True)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    token = get_io_token(test_fc)
    res = accept_terms_and_conditions(token, initiative_id)
    assert res.status_code == 204
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=0, accrued_rewards_increment=0,
                     rewarded_trxs_increment=0, skip_trx_check=True)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    res = pdnd_autocertification(token, initiative_id)
    assert res.status_code == 202
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=0, accrued_rewards_increment=0,
                     rewarded_trxs_increment=0, skip_trx_check=True)
