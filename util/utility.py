import datetime
import os
import random
import time
import uuid
from hashlib import sha256

import pytest

from api.idpay import timeline, enroll_iban, wallet
from api.issuer import enroll
from api.onboarding_io import accept_terms_and_condition, check_prerequisites, pdnd_autocertification, status_onboarding
from api.token_io import login, introspect
from conf.configuration import settings
from util import dataset_utility
from util.certs_loader import load_pm_public_key
from util.dataset_utility import hash_pan, fake_vat
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
    res = introspect(token)
    assert res.json()['fiscal_code'] == fc

    res = accept_terms_and_condition(token, initiative_id)
    assert res.status_code == 204

    res = check_prerequisites(token, initiative_id)
    assert res.status_code == 200

    res = pdnd_autocertification(token, initiative_id)
    assert res.status_code == 202

    res = status_onboarding(token, initiative_id)
    assert res.status_code == 200

    res = retry_io_onboarding(expected='ONBOARDING_OK', request=status_onboarding, token=token,
                              initiative_id=initiative_id, field='status', tries=10, delay=3,
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
    return res


def card_enroll(fc, pan, initiative_id):
    """Enroll a card through API Issuer
        :param fc: Fiscal Code of the citizen
        :param pan: PAN to be enrolled.
        :param initiative_id: ID of the initiative of interest.
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
                         initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                         message='Card not enrolled')
    return res


def retry_io_onboarding(expected, request, token, initiative_id, field, tries=3, delay=5, backoff=1,
                        message='Test failed'):
    count = 0
    res = request(token, initiative_id)
    success = (expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            pytest.fail(f'{message} after {delay * (tries * backoff)}s')
        time.sleep(delay * (count * backoff))
        res = request(token, initiative_id)
        success = (expected == res.json()[field])
    assert expected == res.json()[field]
    return res


def retry_timeline(expected, request, token, initiative_id, field, num_required=1, tries=3, delay=5, backoff=1,
                   message='Test failed'):
    count = 0
    res = request(initiative_id, token)
    success = list(operation[field] for operation in
                   res.json()['operationList']).count(expected) == num_required
    while not success:
        count += 1
        if count == tries:
            pytest.fail(f'{message} after {delay * (tries * backoff)}s')
        time.sleep(delay * (count * backoff))
        res = request(initiative_id, token)
        success = list(operation[field] for operation in
                       res.json()['operationList']).count(expected) == num_required
    assert list(operation[field] for operation in res.json()['operationList']).count(expected) == num_required
    return res


def retry_wallet(expected, request, token, initiative_id, field, tries=3, delay=5, backoff=1,
                 message='Test failed'):
    count = 0
    res = request(initiative_id, token)
    success = (expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            pytest.fail(f'{message} after {delay * (tries * backoff)}s')
        time.sleep(delay * (count * backoff))
        res = request(initiative_id, token)
        success = (expected == res.json()[field])
    assert expected == res.json()[field]
    return res


def expect_wallet_cuonters(expected_amount: float, expected_accrued: float, token: str, initiative_id: str,
                           tries: int = 3, delay: int = 5):
    retry_wallet(expected=expected_amount, request=wallet, token=token,
                 initiative_id=initiative_id, field='amount', tries=tries, delay=delay,
                 message='Wrong amount left')

    retry_wallet(expected=expected_accrued, request=wallet, token=token,
                 initiative_id=initiative_id, field='accrued', tries=tries, delay=delay,
                 message='Wrong accrued amount')


def transactions_hash(transactions: str):
    return f'#sha256sum:{sha256(f"{transactions}".encode()).hexdigest()}'


def custom_transaction(pan: str, amount, curr_date: str = (
        datetime.datetime.now() + datetime.timedelta(hours=random.randint(1, 48))).strftime('%Y-%m-%dT%H:%M:%S.000Z')):
    return f'IDPAY;00;00;{hash_pan(pan)};{curr_date};{uuid.uuid4().int};{uuid.uuid4().int};{uuid.uuid4().int};{amount};978;IDPAY;{uuid.uuid4().int};{uuid.uuid4().int};521870;1234;{dataset_utility.fake_fc()};{fake_vat()};00;{sha256(f"{pan}".encode()).hexdigest().upper()[:29]}'


def clean_trx_files(source_filename: str):
    if os.path.exists(source_filename) and os.path.exists(f'{source_filename}.pgp'):
        os.remove(source_filename)
        os.remove(f'{source_filename}.pgp')
    else:
        print(f'The file {source_filename} and its encrypted version does not exist')
