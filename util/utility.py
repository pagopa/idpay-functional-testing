import datetime
import os
import random
import time
import uuid
from hashlib import sha256

from api.idpay import enroll_iban
from api.idpay import force_reward
from api.idpay import get_iban_info
from api.idpay import get_initiative_statistics
from api.idpay import get_payment_instruments
from api.idpay import get_processed_transactions
from api.idpay import get_reward_content
from api.idpay import remove_payment_instrument
from api.idpay import timeline
from api.idpay import wallet
from api.issuer import enroll
from api.onboarding_io import accept_terms_and_condition
from api.onboarding_io import check_prerequisites
from api.onboarding_io import pdnd_autocertification
from api.onboarding_io import status_onboarding
from api.token_io import introspect
from api.token_io import login
from conf.configuration import settings
from util import dataset_utility
from util.certs_loader import load_pm_public_key
from util.dataset_utility import fake_vat
from util.dataset_utility import hash_pan
from util.dataset_utility import Reward
from util.encrypt_utilities import pgp_string_routine

timeline_operations = settings.IDPAY.endpoints.timeline.operations


def get_io_token(fc):
    """Login through IO
    :param fc: fiscal code to log in.
    """
    return login(fc).content.decode('utf-8')


def onboard_io(fc, initiative_id):
    """Onboarding process through IO
    :param fc: fiscal code to onboard
    :param initiative_id: ID of the initiative of interest.
    """
    token = get_io_token(fc)
    # res = introspect(token)
    # assert res.json()['fiscal_code'] == fc

    res = accept_terms_and_condition(token, initiative_id)
    assert res.status_code == 204

    retry_io_onboarding(expected='ACCEPTED_TC', request=status_onboarding, token=token,
                        initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                        message='Citizen not ACCEPTED_TC')

    res = check_prerequisites(token, initiative_id)
    assert res.status_code == 200

    res = pdnd_autocertification(token, initiative_id)
    assert res.status_code == 202

    res = status_onboarding(token, initiative_id)
    assert res.status_code == 200

    res = retry_io_onboarding(expected='ONBOARDING_OK', request=status_onboarding, token=token,
                              initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                              message='Citizen onboard not OK')
    return res


def iban_enroll(fc, iban, initiative_id):
    """Enroll an IBAN through IO
        :param fc: Fiscal Code of the citizen
        :param iban: IBAN that needs to be enrolled.
        :param initiative_id: ID of the initiative of interest.
        """
    token = get_io_token(fc)
    res = enroll_iban(initiative_id,
                      token,
                      {
                          'iban': iban,
                          'description': 'TEST Bank account'
                      }
                      )
    assert res.status_code == 200

    res = retry_timeline(expected=timeline_operations.add_iban, request=timeline, token=token,
                         initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                         message='IBAN not enrolled')

    retry_iban_info(expected=settings.IDPAY.endpoints.onboarding.iban.unknown_psp, iban=iban, request=get_iban_info,
                    token=token, field='checkIbanStatus', tries=50,
                    delay=0.1, message='Wrong checkIbanStatus')

    return res


def card_enroll(fc, pan, initiative_id, num_required: int = 1):
    """Enroll a card through API Issuer
        :param fc: Fiscal Code of the citizen
        :param pan: PAN to be enrolled.
        :param initiative_id: ID of the initiative of interest.
        :param num_required: required number of card enrollment events.
        """
    res = enroll(initiative_id,
                 fc,
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

    assert res.status_code == 200

    token = get_io_token(fc)
    res = retry_timeline(expected=timeline_operations.add_instrument, request=timeline, token=token,
                         initiative_id=initiative_id, field='operationType', num_required=num_required, tries=50,
                         delay=1, message='Card not enrolled')
    return res


def card_removal(fc, initiative_id, card_position: int = 1):
    """Remove a card through IO
        :param fc: Fiscal Code of the citizen
        :param initiative_id: ID of the initiative of interest.
        :param card_position: position on wallet of the card that needs to be deleted.
        If not specified the first card is deleted.
        """
    token = get_io_token(fc)

    res = get_payment_instruments(initiative_id=initiative_id, token=token)
    assert res.status_code == 200

    instrument_id = res.json()['instrumentList'][card_position - 1]['instrumentId']

    res = remove_payment_instrument(initiative_id=initiative_id, token=token, instrument_id=instrument_id)
    assert res.status_code == 200

    res = retry_timeline(expected=timeline_operations.delete_instrument, request=timeline, token=token,
                         initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                         message='Card not deleted')
    return res


def retry_io_onboarding(expected, request, token, initiative_id, field, tries=3, delay=5,
                        message='Test failed'):
    count = 0
    res = request(token, initiative_id)
    success = (expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(token, initiative_id)
        success = (expected == res.json()[field])
    assert expected == res.json()[field]
    return res


def retry_timeline(expected, request, token, initiative_id, field, num_required=1, tries=3, delay=5,
                   message='Test failed', page: int = 0):
    count = 0
    res = request(initiative_id, token, page)

    operations = []
    for operation in res.json()['operationList']:
        if field in operation:
            if operation[field] == expected:
                operations.append(operation)
    success = len(operations) == num_required

    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(initiative_id, token, page)

        operations = []
        for operation in res.json()['operationList']:
            if field in operation:
                if operation[field] == expected:
                    operations.append(operation)
        success = len(operations) == num_required

    assert success
    return res


def retry_wallet(expected, request, token, initiative_id, field, tries=3, delay=5, message='Test failed'):
    count = 0
    res = request(initiative_id, token)
    success = (expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(initiative_id, token)
        success = (expected == res.json()[field])
    assert expected == res.json()[field]
    return res


def retry_iban_info(expected, iban, request, token, field, tries=3, delay=5, message='Test failed'):
    count = 0
    res = request(iban, token)
    success = False
    if res.status_code == 200:
        success = (expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(iban, token)
        if res.status_code == 200:
            success = (expected == res.json()[field])
    assert expected == res.json()[field]
    return res


def expect_wallet_counters(expected_amount: float, expected_accrued: float, token: str, initiative_id: str,
                           tries: int = 3, delay: int = 5):
    retry_wallet(expected=expected_amount, request=wallet, token=token,
                 initiative_id=initiative_id, field='amount', tries=tries, delay=delay,
                 message='Wrong amount left')

    retry_wallet(expected=expected_accrued, request=wallet, token=token,
                 initiative_id=initiative_id, field='accrued', tries=tries, delay=delay,
                 message='Wrong accrued amount')


def transactions_hash(transactions: str):
    return f'#sha256sum:{sha256(f"{transactions}".encode()).hexdigest()}'


def custom_transaction(pan: str,
                       amount: int,
                       correlation_id: str = None,
                       curr_date: str = None,
                       reversal: bool = False,
                       mcc: str = None):
    if not correlation_id:
        correlation_id = uuid.uuid4().int
    if not curr_date:
        curr_date = (datetime.datetime.utcnow() + datetime.timedelta(seconds=random.randint(10, 60))).strftime(
            '%Y-%m-%dT%H:%M:%S.000Z')
    if not mcc:
        mcc = '1234'

    return f'IDPAY;{"01" if reversal else "00"};00;{hash_pan(pan)};{curr_date};{uuid.uuid4().int};{uuid.uuid4().int};{correlation_id};{amount};978;12345;{uuid.uuid4().int};{uuid.uuid4().int};{pan[:8]};{mcc};{dataset_utility.fake_fc()};{fake_vat()};00;{sha256(f"{pan}".encode()).hexdigest().upper()[:29]}'


def clean_trx_files(source_filename: str):
    if os.path.exists(source_filename) and os.path.exists(f'{source_filename}.pgp'):
        os.remove(source_filename)
        os.remove(f'{source_filename}.pgp')
    else:
        print(f'The file {source_filename} and its encrypted version does not exist')


def check_statistics(organization_id: str,
                     initiative_id: str,
                     old_statistics: dict,
                     onboarded_citizen_count_increment: int,
                     accrued_rewards_increment: float,
                     rewarded_trxs_increment: int = 1,
                     skip_trx_check: bool = False):
    current_statistics = get_initiative_statistics(organization_id=organization_id,
                                                   initiative_id=initiative_id).json()

    assert current_statistics['onboardedCitizenCount'] == old_statistics[
        'onboardedCitizenCount'] + onboarded_citizen_count_increment
    if not skip_trx_check:
        assert current_statistics['rewardedTrxs'] == old_statistics['rewardedTrxs'] + rewarded_trxs_increment
    assert float(current_statistics['accruedRewards'].replace(',', '.')) == round(float(
        old_statistics['accruedRewards'].replace(',', '.')) + accrued_rewards_increment, 2)


def check_rewards(initiative_id,
                  expected_rewards: [Reward],
                  check_absence: bool = False):
    export_ids = []
    organization_id = None
    res = force_reward()
    exported_initiatives = res.json()
    for i in exported_initiatives:
        if i:
            curr_export = i[0]
            if curr_export['initiativeId'] == initiative_id and curr_export['status'] == 'EXPORTED':
                export_ids.append(curr_export['id'])
                organization_id = curr_export['organizationId']

    if check_absence:
        if len(export_ids) == 0:
            return
    else:
        assert len(export_ids) != 0

    for export_id in export_ids:
        res = get_reward_content(organization_id=organization_id, initiative_id=initiative_id, export_id=export_id)
        actual_rewards = res.json()
        for expected_reward in expected_rewards:
            is_rewarded = False
            for r in actual_rewards:
                if r['iban'] == expected_reward.iban:
                    if r['amount'] == expected_reward.amount and r['status'] == 'EXPORTED':
                        is_rewarded = True
            if check_absence:
                assert not is_rewarded
            else:
                assert is_rewarded


def check_processed_transactions(initiative_id,
                                 expected_trx_id: str,
                                 expected_reward: int,
                                 expected_fiscal_code: str,
                                 check_absence: bool = False,
                                 merchant_id: str = 'MERCHANTID',
                                 ):
    res = get_processed_transactions(initiative_id=initiative_id, merchant_id=merchant_id)
    processed_trxs = res.json()['content']
    for trx in processed_trxs:
        if trx['trxId'].strip() == expected_trx_id.strip():
            if trx['fiscalCode'] == expected_fiscal_code:
                if trx['rewardAmount'] == expected_reward:
                    if trx['status'] == 'REWARDED':
                        return
    if check_absence:
        assert True
    else:
        assert False
