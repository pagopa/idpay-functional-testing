import csv
import datetime
import os
import random
import tempfile
import time
import uuid
import zipfile
from hashlib import sha256
from math import floor

import pandas as pd

from api.idpay import delete_initiative
from api.idpay import enroll_iban
from api.idpay import force_reward
from api.idpay import get_iban_info
from api.idpay import get_initiative_statistics
from api.idpay import get_initiative_statistics_merchant_portal
from api.idpay import get_merchant_list
from api.idpay import get_merchant_processed_transactions
from api.idpay import get_merchant_unprocessed_transactions
from api.idpay import get_payment_dispositions_export_content
from api.idpay import get_payment_instruments
from api.idpay import get_ranking_page
from api.idpay import get_reward_content
from api.idpay import obtain_selfcare_test_token
from api.idpay import post_initiative_info
from api.idpay import publish_approved_initiative
from api.idpay import put_citizen_readmission
from api.idpay import put_citizen_suspension
from api.idpay import put_initiative_approval
from api.idpay import put_initiative_beneficiary_info
from api.idpay import put_initiative_general_info
from api.idpay import put_initiative_refund_info
from api.idpay import put_initiative_reward_info
from api.idpay import put_payment_results
from api.idpay import remove_payment_instrument
from api.idpay import timeline
from api.idpay import unsubscribe
from api.idpay import upload_merchant_csv
from api.idpay import upload_whitelist_csv
from api.idpay import wallet
from api.issuer import enroll
from api.onboarding_io import accept_terms_and_conditions
from api.onboarding_io import check_prerequisites
from api.onboarding_io import pdnd_autocertification
from api.onboarding_io import status_onboarding
from api.pdv import detokenize_pdv_token
from api.pdv import get_pdv_token
from api.token_io import login
from conf.configuration import secrets
from conf.configuration import settings
from util import dataset_utility
from util.certs_loader import load_pm_public_key
from util.dataset_utility import fake_iban
from util.dataset_utility import fake_merchant_file
from util.dataset_utility import fake_vat
from util.dataset_utility import hash_pan
from util.dataset_utility import merchantInfo
from util.dataset_utility import reward
from util.dataset_utility import serialize
from util.encrypt_utilities import pgp_string_routine

PAYMENT_OK = 'OK - ORDINE ESEGUITO'
PAYMENT_KO = 'KO'
REJECT_REASON = 'IBAN NOT VALID'
reward_columns = [
    'uniqueID',
    'result',
    'rejectionReason',
    'cro',
    'executionDate'
]

timeline_operations = settings.IDPAY.endpoints.timeline.operations
wallet_statuses = settings.IDPAY.endpoints.wallet.statuses


def get_io_token(fc):
    """Login through IO
    :param fc: fiscal code to log in.
    """
    return login(fc).content.decode('utf-8')


def get_selfcare_token(institution_info: str):
    """Login through Self Care mock
    :param institution_info: Information of the institute to log in.
    """
    return obtain_selfcare_test_token(institution_info).content.decode('utf-8')


def onboard_io(fc, initiative_id):
    """Onboarding process through IO
    :param fc: fiscal code to onboard
    :param initiative_id: ID of the initiative of interest.
    """
    token = get_io_token(fc)

    res = accept_terms_and_conditions(token, initiative_id)
    assert res.status_code == 204

    retry_io_onboarding(expected='ACCEPTED_TC', request=status_onboarding, token=token,
                        initiative_id=initiative_id, field='status', tries=50, delay=1,
                        message='Citizen not ACCEPTED_TC')

    res = check_prerequisites(token, initiative_id)
    assert res.status_code == 200

    res = pdnd_autocertification(token, initiative_id)
    assert res.status_code == 202

    res = status_onboarding(token, initiative_id)
    assert res.status_code == 200

    res = retry_io_onboarding(expected='ONBOARDING_OK', request=status_onboarding, token=token,
                              initiative_id=initiative_id, field='status', tries=50, delay=1,
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

    retry_iban_info(expected=settings.IDPAY.endpoints.onboarding.iban.mocked_ok, iban=iban, request=get_iban_info,
                    token=token, field='checkIbanStatus', tries=50,
                    delay=1)

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

    if res.status_code == 404:
        res = request(initiative_id, token, page)
        while res.status_code == 404:
            time.sleep(delay)
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


def retry_wallet(expected, request, token, initiative_id, field, tries=3, delay=5):
    count = 0
    res = request(initiative_id, token)
    success = (res.status_code == 200 and expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(initiative_id, token)
        success = (res.status_code == 200 and expected == res.json()[field])
    assert success
    return res


def retry_iban_info(expected, iban, request, token, field, tries=3, delay=5):
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
                 initiative_id=initiative_id, field='amount', tries=tries, delay=delay)

    retry_wallet(expected=expected_accrued, request=wallet, token=token,
                 initiative_id=initiative_id, field='accrued', tries=tries, delay=delay)


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


def retry_institution_statistics(initiative_id: str,
                                 tries=10,
                                 delay=1):
    count = 0

    res = get_initiative_statistics(
        organization_id=secrets.organization_id,
        initiative_id=initiative_id)

    while res.status_code != 200:
        count += 1
        time.sleep(delay)
        res = get_initiative_statistics(
            organization_id=secrets.organization_id,
            initiative_id=initiative_id)
        if count == tries:
            break

    assert res.status_code == 200
    return res.json()


def retry_publishing_initiative(selfcare_token: str,
                                initiative_id: str,
                                tries=10,
                                delay=3):
    count = 0
    res = publish_approved_initiative(selfcare_token=selfcare_token,
                                      initiative_id=initiative_id)

    while res.status_code != 204:
        count += 1
        time.sleep(delay)
        res = publish_approved_initiative(selfcare_token=selfcare_token,
                                          initiative_id=initiative_id)
        if count == tries:
            break

    assert res.status_code == 204


def retry_merchant_statistics(initiative_id: str,
                              merchant_id: str,
                              tries=10,
                              delay=1):
    count = 0

    res = get_initiative_statistics_merchant_portal(
        merchant_id=merchant_id,
        initiative_id=initiative_id)

    while res.status_code != 200:
        count += 1
        time.sleep(delay)
        res = get_initiative_statistics_merchant_portal(
            merchant_id=merchant_id,
            initiative_id=initiative_id)
        if count == tries:
            break

    assert res.status_code == 200
    return res.json()


def check_statistics(organization_id: str,
                     initiative_id: str,
                     old_statistics: dict,
                     onboarded_citizen_count_increment: int,
                     accrued_rewards_increment: float,
                     rewarded_trxs_increment: int = 1,
                     skip_trx_check: bool = False,
                     tries=10,
                     delay=1):
    success = False
    count = 0

    while not success:

        current_statistics = get_initiative_statistics(organization_id=organization_id,
                                                       initiative_id=initiative_id).json()
        are_onboards_incremented = (current_statistics['onboardedCitizenCount'] == old_statistics[
            'onboardedCitizenCount'] + onboarded_citizen_count_increment)

        are_accrued_rewards_incremented = (float(current_statistics['accruedRewards']) == round(float(
            old_statistics['accruedRewards']) + accrued_rewards_increment, 2))

        if not skip_trx_check:
            are_trxs_incremented = (
                    current_statistics['rewardedTrxs'] == old_statistics['rewardedTrxs'] + rewarded_trxs_increment)
        else:
            are_trxs_incremented = True

        success = are_onboards_incremented and are_accrued_rewards_incremented and are_trxs_incremented
        time.sleep(delay)
        count += 1
        if count == tries:
            break

    assert success


def check_merchant_statistics(merchant_id: str,
                              initiative_id: str,
                              old_statistics: dict,
                              accrued_rewards_increment: float,
                              refunded_increment: float = 0,
                              tries=10,
                              delay=1):
    success = False
    count = 0

    while not success:
        current_merchant_statistics = get_initiative_statistics_merchant_portal(merchant_id=merchant_id,
                                                                                initiative_id=initiative_id).json()
        are_accrued_rewards_incremented = (current_merchant_statistics['accrued'] == old_statistics[
            'accrued'] + accrued_rewards_increment)
        are_refunded_incremented = (current_merchant_statistics['refunded'] == old_statistics[
            'refunded'] + refunded_increment)
        success = are_accrued_rewards_incremented and are_refunded_incremented
        time.sleep(delay)
        count += 1
        if count == tries:
            break

    assert success


def force_rewards(initiative_id,
                  check_absence: bool = False):
    export_ids = []
    export_path = None

    res = force_reward()
    exported_initiatives = res.json()
    for i in exported_initiatives:
        if i:
            curr_export = i[0]
            if curr_export['initiativeId'] == initiative_id and curr_export['status'] == 'EXPORTED':
                export_ids.append(curr_export['id'])
                export_path = curr_export['filePath']
                assert export_path.split('/')[1] == initiative_id

    if check_absence:
        assert len(export_ids) == 0
    else:
        assert len(export_ids) != 0

    return [export_ids, export_path]


def check_rewards(initiative_id: str,
                  organization_id: str,
                  export_ids: [str],
                  expected_rewards: [reward],
                  check_absence: bool = False,
                  exptected_status: str = 'EXPORTED',
                  delay=3,
                  tries=10):
    success = False
    count = 0

    while not success:
        for export_id in export_ids:
            res = get_reward_content(organization_id=organization_id, initiative_id=initiative_id, export_id=export_id)
            actual_rewards = res.json()
            for expected_reward in expected_rewards:
                is_rewarded = False
                for r in actual_rewards:
                    if (r['iban'] == expected_reward.iban and r['status'] == exptected_status
                            and r['amount'] == expected_reward.amount):
                        assert not is_rewarded
                        is_rewarded = True

                if check_absence:
                    success = not is_rewarded
                else:
                    success = is_rewarded
        if not success:
            time.sleep(delay)
            count += 1
        if count == tries:
            break
    assert success


def get_payment_disposition_unique_ids(payment_dispositions, fiscal_code, expected_reward: reward):
    unique_ids = []
    total_amount = 0
    for disposition in payment_dispositions:
        if str(disposition[2]) == str(fiscal_code) and str(disposition[4]) == expected_reward.iban:
            unique_ids.append(disposition[1])
            total_amount += float(disposition[5])
    assert floor(total_amount) == expected_reward.amount * 100
    return unique_ids


def check_unprocessed_transactions(initiative_id,
                                   expected_trx_id: str,
                                   expected_effective_amount: int,
                                   expected_reward_amount: int,
                                   expected_fiscal_code: str = 'UNDEFINED',
                                   merchant_id: str = 'MERCHANTID',
                                   expected_status: str = 'UNDEFINED',
                                   check_absence: bool = False
                                   ):
    res = get_merchant_unprocessed_transactions(initiative_id=initiative_id, merchant_id=merchant_id)
    assert res.status_code == 200
    processed_trxs = res.json()['content']
    for trx in processed_trxs:
        if trx['trxId'].strip() == expected_trx_id.strip():
            if trx['effectiveAmount'] == expected_effective_amount:
                if trx['rewardAmount'] == expected_reward_amount:
                    if trx['status'] == expected_status:
                        if expected_status == 'CREATED':
                            return
                        elif trx['fiscalCode'] == expected_fiscal_code:
                            return
    if check_absence:
        assert True
    else:
        assert False


def check_processed_transactions(initiative_id,
                                 expected_trx_id: str,
                                 expected_reward: int,
                                 expected_fiscal_code: str,
                                 check_absence: bool = False,
                                 merchant_id: str = 'MERCHANTID',
                                 ):
    res = get_merchant_processed_transactions(initiative_id=initiative_id, merchant_id=merchant_id)
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


def merchant_id_from_fc(initiative_id: str,
                        desired_fc: str,
                        tries=20,
                        delay=5):
    success = False
    count = 0
    selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)

    while not success:
        res = get_merchant_list(selfcare_token=selfcare_token, initiative_id=initiative_id)
        content = res.json()['content']
        i = 1
        while content:
            for merchant in content:
                if merchant['fiscalCode'] == desired_fc:
                    return merchant['merchantId']
            res = get_merchant_list(selfcare_token=selfcare_token, initiative_id=initiative_id, page=i)
            content = res.json()['content']
            i += 1
        count += 1
        time.sleep(delay)
        if count == tries:
            break
    return None


def natural_language_to_date_converter(natural_language_date: str):
    if natural_language_date == 'today':
        actual_date = datetime.datetime.now().strftime('%Y-%m-%d')
    elif natural_language_date == 'tomorrow':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    elif natural_language_date == 'ten_days_from_tomorrow':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=12)).strftime('%Y-%m-%d')
    elif natural_language_date == 'day_after_tomorrow':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    elif natural_language_date == 'future':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=365 * 5)).strftime('%Y-%m-%d')
    elif natural_language_date == 'future_tomorrow':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=365 * 5 + 1)).strftime('%Y-%m-%d')
    else:
        actual_date = datetime.datetime.strptime(natural_language_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    return actual_date


def create_initiative(initiative_name_in_settings: str,
                      known_beneficiaries: list = None):
    creation_payloads = settings.initiatives[initiative_name_in_settings].creation_payloads

    institution_selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    initiative_id = post_initiative_info(selfcare_token=institution_selfcare_token).json()['initiativeId']

    if 'rankingStartDate' in creation_payloads.general:
        creation_payloads.general['rankingStartDate'] = natural_language_to_date_converter(
            creation_payloads.general['rankingStartDate'])
    if 'rankingEndDate' in creation_payloads.general:
        creation_payloads.general['rankingEndDate'] = natural_language_to_date_converter(
            creation_payloads.general['rankingEndDate'])

    creation_payloads.general['startDate'] = natural_language_to_date_converter(creation_payloads.general['startDate'])
    creation_payloads.general['endDate'] = natural_language_to_date_converter(creation_payloads.general['endDate'])

    res = put_initiative_general_info(selfcare_token=institution_selfcare_token,
                                      initiative_id=initiative_id,
                                      general_payload=creation_payloads.general)
    assert res.status_code == 204

    if creation_payloads.general['beneficiaryKnown'] is True:
        res = upload_whitelist_file(selfcare_token=institution_selfcare_token,
                                    initiative_id=initiative_id,
                                    fiscal_codes=known_beneficiaries)
        assert res.status_code == 200
        time.sleep(5)
    else:
        res = put_initiative_beneficiary_info(selfcare_token=institution_selfcare_token,
                                              initiative_id=initiative_id,
                                              beneficiary_payload=creation_payloads.beneficiary)
        assert res.status_code == 204

    res = put_initiative_reward_info(selfcare_token=institution_selfcare_token,
                                     initiative_id=initiative_id,
                                     reward_payload=creation_payloads.reward
                                     )
    assert res.status_code == 204

    res = put_initiative_refund_info(selfcare_token=institution_selfcare_token,
                                     initiative_id=initiative_id,
                                     refund_payload=creation_payloads.refund
                                     )
    assert res.status_code == 204

    pagopa_selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.PagoPA)
    res = put_initiative_approval(selfcare_token=pagopa_selfcare_token,
                                  initiative_id=initiative_id)
    assert res.status_code == 204

    institution_selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)

    retry_publishing_initiative(selfcare_token=institution_selfcare_token, initiative_id=initiative_id)

    return initiative_id


def create_initiative_and_update_conf(initiative_name: str,
                                      known_beneficiaries: list = None):
    secrets.initiatives[initiative_name]['id'] = create_initiative(initiative_name_in_settings=initiative_name,
                                                                   known_beneficiaries=known_beneficiaries)
    print(f'Created initiative {secrets.initiatives[initiative_name]["id"]} ({initiative_name})')
    secrets['newly_created'].add(secrets.initiatives[initiative_name]['id'])

    startup_time = settings.INITIATIVE_STARTUP_TIME_SECONDS
    if 'initiative_startup_time_seconds' in settings.initiatives[initiative_name]:
        startup_time = settings.initiatives[initiative_name]['initiative_startup_time_seconds']
    time.sleep(startup_time)


def onboard_one_random_merchant(initiative_id: str,
                                institution_selfcare_token: str):
    fc = fake_vat()
    vat = fc
    iban = fake_iban('00000')
    merchant_csv = fake_merchant_file(acquirer_id=settings.idpay.acquirer_id,
                                      merchants_info=[merchantInfo(vat=vat, fc=fc, iban=iban)])

    csv_file_path = f'merchant_{datetime.datetime.now().strftime("%Y%m%d.%H%M%S")}.csv'

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for info_row in merchant_csv:
            writer.writerow([info_row])

    merchant_csv_upload_payload = {'file': (csv_file_path, open(csv_file_path, 'rb'), 'text/csv')}

    res = upload_merchant_csv(selfcare_token=institution_selfcare_token,
                              initiative_id=initiative_id,
                              merchants_payload=merchant_csv_upload_payload
                              )
    assert res.status_code == 200

    curr_merchant_id = merchant_id_from_fc(initiative_id=initiative_id,
                                           desired_fc=fc)
    assert curr_merchant_id is not None

    os.remove(csv_file_path)

    return {
        'id': curr_merchant_id,
        'iban': iban,
        'fiscal_code': fc
    }


def tokenize_fc(fiscal_code: str):
    res = get_pdv_token(fiscal_code=fiscal_code)
    assert res.status_code == 200
    token = res.json()['token']
    res = detokenize_pdv_token(token=token)
    assert res.json()['pii'] == fiscal_code
    return token


def detokenize_to_fc(token: str):
    res = detokenize_pdv_token(token=token)
    assert res.status_code == 200
    fiscal_code = res.json()['pii']
    res = get_pdv_token(fiscal_code=fiscal_code)
    assert res.status_code == 200
    assert res.json()['token'] == token
    return fiscal_code


def suspend_citizen_from_initiative(initiative_id: str,
                                    fiscal_code: str):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = put_citizen_suspension(selfcare_token=institution_token, initiative_id=initiative_id, fiscal_code=fiscal_code)
    assert res.status_code == 204
    return res


def readmit_citizen_to_initiative(initiative_id: str,
                                  fiscal_code: str):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = put_citizen_readmission(selfcare_token=institution_token, initiative_id=initiative_id,
                                  fiscal_code=fiscal_code)
    assert res.status_code == 204
    return res


def citizen_unsubscribe_from_initiative(initiative_id: str,
                                        fiscal_code: str):
    token = get_io_token(fiscal_code)
    res = unsubscribe(initiative_id, token)
    assert res.status_code == 204
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    retry_timeline(expected=timeline_operations.unsubscribed, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Not unsubscribed')


def retry_payment_instrument(expected_type, expected_status, request, token, initiative_id, field_type, field_status,
                             num_required=1, tries=3, delay=5):
    count = 0
    res = request(initiative_id, token)
    assert res.status_code == 200

    instruments = []
    for instrument in res.json()['instrumentList']:
        if field_type in instrument:
            if instrument[field_type] == expected_type and instrument[field_status] == expected_status:
                instruments.append(instrument)
    success = len(instruments) == num_required

    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(initiative_id, token)

        instruments = []
        for instrument in res.json()['instrumentList']:
            if field_type in instrument:
                if instrument[field_type] == expected_type and instrument[field_status] == expected_status:
                    instruments.append(instrument)
        success = len(instruments) == num_required
    assert success
    return res


def delete_new_initiatives_after_test():
    if not settings.KEEP_INITIATIVES_AFTER_TEST:
        for initiative_id in secrets['newly_created']:
            res = delete_initiative(initiative_id=initiative_id)
            if res.status_code == 204:
                print(
                    f'Deleted initiative {initiative_id}')
            else:
                print(
                    f'Failed to delete initiative {initiative_id}')


def get_refund_exported_content(initiative_id: str,
                                exported_file_name: str):
    selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)

    res = get_payment_dispositions_export_content(selfcare_token=selfcare_token,
                                                  initiative_id=initiative_id,
                                                  exported_file_name=exported_file_name)
    assert res.status_code == 200

    with tempfile.TemporaryFile() as tmp:
        tmp.write(res.content)
        with zipfile.ZipFile(tmp) as zipped_input_file:
            extracted_file = zipped_input_file.infolist()[0].filename
            extraction_path = os.path.join(initiative_id, extracted_file)
            zipped_input_file.extractall(path=initiative_id)

    with open(extraction_path, 'r') as input_file:
        payment_exports = pd.read_csv(input_file, quotechar='"', sep=';')
        payment_exports_list = list(payment_exports.values)

    return payment_exports_list


def generate_payment_results(
        payment_disposition_unique_ids: [str],
        success: bool = True):
    refunds = []
    payment_result = PAYMENT_OK
    reject_reason = ''

    if not success:
        payment_result = PAYMENT_KO
        reject_reason = REJECT_REASON

    for unique_id in payment_disposition_unique_ids:
        refunds.append([
            unique_id,
            payment_result,
            reject_reason,
            sha256(f'{unique_id}'.encode()).hexdigest(),
            datetime.datetime.now().strftime('%Y-%m-%d')
        ])

    output_file_name = 'payment-results-' + datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    ourput_file_path = os.path.join('.', output_file_name)

    serialize(refunds, reward_columns, ourput_file_path + '.csv', True)

    with zipfile.ZipFile(ourput_file_path + '.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(ourput_file_path + '.csv', arcname=output_file_name + '.csv')

    return ourput_file_path + '.zip'


def upload_payment_results(
        initiative_id: str,
        payment_result_name: str):
    selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    with open(payment_result_name, 'rb') as f:
        res = put_payment_results(selfcare_token=selfcare_token,
                                  initiative_id=initiative_id,
                                  results_file_name=payment_result_name,
                                  results_file=f)
        assert res.status_code == 201
        return res


def check_ranking_status_institution_portal(initiative_id: str,
                                            desired_fc: str,
                                            desired_status: str):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = get_ranking_page(selfcare_token=institution_token, initiative_id=initiative_id, page=0)
    content = res.json()['content']
    i = 1
    while content:
        for beneficiary in content:
            if beneficiary['beneficiary'] == desired_fc:
                if beneficiary['beneficiaryRankingStatus'] == desired_status:
                    return True
        res = get_merchant_list(selfcare_token=institution_token, initiative_id=initiative_id, page=i)
        content = res.json()['content']
        i += 1
    return False


def upload_whitelist_file(selfcare_token: str,
                          initiative_id: str,
                          fiscal_codes: list):
    csv_file_path = f'fiscal_codes_{datetime.datetime.now().strftime("%Y%m%d.%H%M%S")}.csv'

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for fc in fiscal_codes:
            writer.writerow([fc])

    whitelist_csv_upload_payload = {'file': (csv_file_path, open(csv_file_path, 'rb'), 'text/csv')}

    return upload_whitelist_csv(selfcare_token=selfcare_token,
                                initiative_id=initiative_id,
                                whitelist_payload=whitelist_csv_upload_payload
                                )
