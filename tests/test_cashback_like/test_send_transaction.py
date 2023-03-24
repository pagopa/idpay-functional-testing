import random
import time
from math import floor

import pytest

from api.idpay import timeline, wallet
from api.issuer import enroll
from conf.configuration import secrets, settings
from util import dataset_utility
from util.certs_loader import load_pm_public_key
from util.dataset_utility import fake_fc, fake_pan
from util.encrypt_utilities import pgp_string_routine
from util.transaction_upload import encrypt_and_upload
from util.utility import onboard_io, card_enroll, get_io_token, iban_enroll, retry_timeline, transactions_hash, \
    custom_transaction, clean_trx_files

initiative_id = secrets.initiatives.cashback_like.id
cashback_percentage = settings.initiatives.cashback_like.cashback_percentage
budget_per_citizen = settings.initiatives.cashback_like.budget_per_citizen
max_amount = (budget_per_citizen / cashback_percentage * 100) * 100


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

    # Send the transaction with an amount greater than the amount awarded with budget_per_citizen
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

    assert res.json()['accrued'] == budget_per_citizen

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

    assert res.json()['accrued'] == budget_per_citizen

    # Send a second transaction
    amount = floor(random.random() * max_amount)

    transaction = custom_transaction(pan, amount)
    transactions_hash(transaction)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    time.sleep(random.randint(5, 10))

    res = wallet(initiative_id, token)

    assert res.json()['accrued'] == budget_per_citizen

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 1

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('2')
def test_send_50_transaction_erode_budget():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()

    min_amount = 340.833885

    assert onboard_io(test_fc, initiative_id).json()['status'] == 'ONBOARDING_OK'
    assert list(operation['operationType'] for operation in
                card_enroll(test_fc, pan, initiative_id).json()['operationList']).count('ADD_INSTRUMENT') == 1

    token = get_io_token(test_fc)
    assert list(operation['operationType'] for operation in
                iban_enroll(token, curr_iban, initiative_id).json()['operationList']).count('ADD_IBAN') == 1

    # Send the transactions
    transactions = []
    for i in range(50):
        amount = floor(random.random() * max_amount + min_amount)
        transactions.append(custom_transaction(pan, amount))
    trx_file_content = '\n'.join(transactions)
    trx_file_content_complete = '\n'.join([transactions_hash(trx_file_content), trx_file_content])

    res, curr_file_name = encrypt_and_upload(trx_file_content_complete)
    assert res.status_code == 201

    retry_timeline(expected='TRANSACTION', request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    time.sleep(random.randint(5, 10))

    res = timeline(initiative_id, token)

    assert 'TRANSACTION' in list(operation['operationType'] for operation in res.json()['operationList'])

    expected_accrued = budget_per_citizen

    res = wallet(initiative_id, token)

    assert res.json()['amount'] == 0
    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('3')
def test_send_transaction_200e_erode_budget():
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
    amount = 20000
    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    retry_timeline(expected='TRANSACTION', request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 1

    expected_accrued = budget_per_citizen

    res = wallet(initiative_id, token)

    assert res.json()['amount'] == 0
    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('4')
def test_send_transaction_100e_150e_erode_budget():
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
    amount1 = 10000
    amount2 = 15000
    transaction1 = custom_transaction(pan, amount1)
    transaction2 = custom_transaction(pan, amount2)
    trx_file1_content = '\n'.join([transaction1, transaction2])
    trx_file1_content_complete = '\n'.join([transactions_hash(trx_file1_content), trx_file1_content])

    res, curr_file_name = encrypt_and_upload(trx_file1_content_complete)
    assert res.status_code == 201

    retry_timeline(expected='TRANSACTION', request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    time.sleep(random.randint(5, 10))

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 2

    expected_accrued = budget_per_citizen

    res = wallet(initiative_id, token)

    assert res.json()['amount'] == 0
    assert res.json()['accrued'] == expected_accrued

    amount3 = 3500

    transaction3 = custom_transaction(pan, amount3)
    trx_file2_content_complete = '\n'.join([transactions_hash(transaction3), transaction3])

    res, curr_file_name = encrypt_and_upload(trx_file2_content_complete)
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 2

    expected_accrued = budget_per_citizen

    res = wallet(initiative_id, token)

    assert res.json()['amount'] == 0
    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('5')
def test_send_transaction_ko_card_enroll():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()

    assert onboard_io(test_fc, initiative_id).json()['status'] == 'ONBOARDING_OK'

    res = enroll(initiative_id,
                 test_fc,
                 {
                     "brand": "VISA",
                     "type": "DEB",
                     "pgpPan": pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     "expireMonth": "08",
                     "expireYear": "2023",
                     "issuerAbiCode": "",
                     "holder": "TEST"
                 }
                 )
    print(res.status_code)
    assert res.status_code != 200

    token = get_io_token(test_fc)
    assert list(operation['operationType'] for operation in
                iban_enroll(token, curr_iban, initiative_id).json()['operationList']).count('ADD_IBAN') == 1

    # Send the transaction
    amount = 2750

    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 0

    expected_accrued = 0

    res = wallet(initiative_id, token)

    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)
