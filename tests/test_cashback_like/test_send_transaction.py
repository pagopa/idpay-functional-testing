import random
import time
from math import floor

import pytest

from api.idpay import timeline, wallet
from conf.configuration import secrets, settings
from util import dataset_utility
from util.dataset_utility import fake_fc, fake_pan
from util.transaction_upload import encrypt_and_upload
from util.utility import onboard_io, card_enroll, get_io_token, iban_enroll, retry_timeline, transactions_hash, \
    custom_transaction, clean_trx_files

initiative_id = secrets.initiatives.cashback_like.id
cashback_percentage = settings.initiatives.cashback_like.cashback_percentage
max_cashback = settings.initiatives.cashback_like.max_cashback
max_amount = (max_cashback / cashback_percentage * 100) * 100


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('1.4.0')
def test_send_transaction():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()

    assert onboard_io(test_fc, initiative_id).json()['status'] == 'ONBOARDING_OK'
    assert list(operation['operationType'] for operation in
                card_enroll(test_fc, pan, initiative_id).json()['operationList']).count('ADD_INSTRUMENT') == 1

    token = get_io_token(test_fc)
    assert list(operation['operationType'] for operation in
                iban_enroll(token, curr_iban, initiative_id).json()['operationList']).count('ADD_IBAN') == 1

    # Send the transaction
    amount = floor(random.random() * max_amount)

    transaction = custom_transaction(pan, amount)
    transactions_hash(transaction)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    retry_timeline(expected='TRANSACTION', request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 1

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)

    res = wallet(initiative_id, token)

    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('1.4.1')
def test_send_transaction_award_max():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()

    assert onboard_io(test_fc, initiative_id).json()['status'] == 'ONBOARDING_OK'
    assert list(operation['operationType'] for operation in
                card_enroll(test_fc, pan, initiative_id).json()['operationList']).count('ADD_INSTRUMENT') == 1

    token = get_io_token(test_fc)
    assert list(
        operation['operationType'] for operation in
        iban_enroll(token, curr_iban, initiative_id).json()['operationList']).count('ADD_IBAN') == 1

    # Send the transaction with an amount greater than the amount awarded with max_cashback
    amount = floor(max_amount + random.randint(1, 999999))

    transaction = custom_transaction(pan, amount)
    transactions_hash(transaction)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    retry_timeline(expected='TRANSACTION', request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 1

    res = wallet(initiative_id, token)

    assert res.json()['accrued'] == max_cashback

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('1.4.2')
def test_send_transactions_award_only_one():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()

    assert onboard_io(test_fc, initiative_id).json()['status'] == 'ONBOARDING_OK'
    assert list(operation['operationType'] for operation in
                card_enroll(test_fc, pan, initiative_id).json()['operationList']).count('ADD_INSTRUMENT') == 1

    token = get_io_token(test_fc)
    assert list(
        operation['operationType'] for operation in
        iban_enroll(token, curr_iban, initiative_id).json()['operationList']).count('ADD_IBAN') == 1

    # Send the transaction
    amount = floor(max_amount + random.randint(1, 999999))

    transaction = custom_transaction(pan, amount)
    transactions_hash(transaction)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    retry_timeline(expected='TRANSACTION', request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 1

    res = wallet(initiative_id, token)

    assert res.json()['accrued'] == max_cashback

    # Send a second transaction
    amount = floor(random.random() * max_amount)

    transaction = custom_transaction(pan, amount)
    transactions_hash(transaction)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    time.sleep(random.randint(5, 10))

    res = wallet(initiative_id, token)

    assert res.json()['accrued'] == max_cashback

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 1

    clean_trx_files(curr_file_name)
