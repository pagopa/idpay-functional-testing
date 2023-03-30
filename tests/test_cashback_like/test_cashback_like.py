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
    custom_transaction, clean_trx_files, retry_wallet, expect_wallet_cuonters

initiative_id = secrets.initiatives.cashback_like.id
cashback_percentage = settings.initiatives.cashback_like.cashback_percentage
budget_per_citizen = settings.initiatives.cashback_like.budget_per_citizen
max_amount = (budget_per_citizen / cashback_percentage * 100) * 100

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses
timeline_operations = settings.IDPAY.endpoints.timeline.operations


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.2')
def test_send_single_transaction():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 1.2.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not subscribed')
    # 1.2.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Card not enrolled')

    # 1.2.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='IBAN not enrolled')

    amount = floor(random.random() * max_amount)
    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.2.4
    assert res.status_code == 201
    # 1.2.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.2.4
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.3')
def test_send_50_transaction_erode_budget_max_award():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    min_amount = 340.833885

    # 1.3.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not subscribed')
    # 1.3.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Card not enrolled')

    # 1.3.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='IBAN not enrolled')

    transactions = []
    for i in range(50):
        amount = floor(random.random() * max_amount + min_amount)
        transactions.append(custom_transaction(pan, amount))
    trx_file_content = '\n'.join(transactions)
    trx_file_content_complete = '\n'.join([transactions_hash(trx_file_content), trx_file_content])

    res, curr_file_name = encrypt_and_upload(trx_file_content_complete)
    # 1.3.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    expected_accrued = budget_per_citizen
    expected_amount_left = 0
    # 1.3.4
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.4')
def test_send_single_200e_transaction_erode_budget_max_award():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 1.4.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not subscribed')
    # 1.4.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Card not enrolled')

    # 1.4.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='IBAN not enrolled')

    amount = 20000
    transaction = custom_transaction(pan, amount)
    transactions_hash(transaction)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.4.4
    assert res.status_code == 201
    # 1.4.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = 0
    # 1.4.4
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.5')
def test_not_award_after_budget_erosion():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 1.5.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not subscribed')
    # 1.5.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Card not enrolled')

    # 1.5.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='IBAN not enrolled')

    amount1 = 10000
    amount2 = 15000
    transaction1 = custom_transaction(pan, amount1)
    transaction2 = custom_transaction(pan, amount2)
    trx_file1_content = '\n'.join([transaction1, transaction2])
    trx_file1_content_complete = '\n'.join([transactions_hash(trx_file1_content), trx_file1_content])

    res, curr_file_name = encrypt_and_upload(trx_file1_content_complete)
    # 1.5.4
    assert res.status_code == 201
    # 1.5.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = 0
    # 1.5.4
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = 3500
    transaction3 = custom_transaction(pan, amount3)
    trx_file2_content_complete = '\n'.join([transactions_hash(transaction3), transaction3])
    res, curr_file_name = encrypt_and_upload(trx_file2_content_complete)
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 1.5.6
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = 0
    # 1.5.6
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.6')
def test_award_again_after_reversal():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    curr_amount = floor(3408.33885)
    num_trx = 5

    # 1.6.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not subscribed')
    # 1.6.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Card not enrolled')

    # 1.6.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='IBAN not enrolled')

    transactions = []
    for i in range(num_trx):
        transactions.append(custom_transaction(pan=pan, amount=curr_amount))
    # Save latest transaction's correlation ID to use it in reversal transaction
    latest_trx_correlation_id = transactions[num_trx - 1].split(';')[7]
    trx_file_content = '\n'.join(transactions)
    trx_file_content_complete = '\n'.join([transactions_hash(trx_file_content), trx_file_content])
    res, curr_file_name = encrypt_and_upload(trx_file_content_complete)
    # 1.6.4
    assert res.status_code == 201

    # 1.6.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=num_trx,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = 0
    # 1.6.5
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount = 920
    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.6.8
    assert res.status_code == 201
    # 1.6.8
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=num_trx,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction received')
    # 1.6.9
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    reversal_transaction = custom_transaction(pan=pan, amount=curr_amount, correlation_id=latest_trx_correlation_id,
                                              reversal=True)
    trx_file_content = '\n'.join([transactions_hash(reversal_transaction), reversal_transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.6.11
    assert res.status_code == 201
    # 1.6.11
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal not received')

    expected_reversal = round(floor(curr_amount * cashback_percentage) / 10000, 2)
    expected_accrued = budget_per_citizen - expected_reversal
    expected_amount_left = expected_reversal
    # 1.6.12
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount = 1050
    transaction = custom_transaction(pan=pan, amount=amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.6.13
    assert res.status_code == 201
    # 1.6.13
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=num_trx + 1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = round(budget_per_citizen - expected_reversal + floor(amount * cashback_percentage) / 10000, 2)
    expected_amount_left = round(budget_per_citizen - expected_accrued, 2)
    # 1.6.14
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.7')
def test_send_transaction_ko_card_enroll():
    test_fc = fake_fc()
    curr_iban = dataset_utility.fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 1.7.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not subscribed')

    # issuerAbiCode is blank to simulate IBAN enrollment failure
    res = enroll(initiative_id,
                 test_fc,
                 {
                     'brand': 'VISA',
                     'type': 'DEB',
                     'pgpPan': pgp_string_routine(pan, load_pm_public_key()).decode('unicode_escape'),
                     'expireMonth': '08',
                     'expireYear': '2023',
                     'issuerAbiCode': '',
                     'holder': 'TEST'
                 }
                 )
    # 1.7.2
    assert res.status_code != 200
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not subscribed')
    retry_timeline(expected=timeline_operations.ADD_INSTRUMENT, request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', num_required=0, tries=3, delay=3,
                   message='IBAN not enrolled')

    # 1.7.3
    iban_enroll(test_fc, curr_iban, initiative_id)

    # 1.7.4
    retry_timeline(expected=timeline_operations.add_iban, request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', num_required=1, tries=3, delay=3,
                   message='IBAN not enrolled')

    # Send the transaction
    amount = 2750

    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.7.5
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 1.7.5
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = budget_per_citizen
    # 1.7.5
    expect_wallet_cuonters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('7')
def test_send_small_amount_no_refund():
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
    amount = floor(random.randint(1, 3))

    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 0

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)

    res = wallet(initiative_id, token)

    assert res.json()['amount'] == budget_per_citizen
    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('8')
def test_send_minimum_awardable_amount():
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
    amount = floor(4)

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

    assert res.json()['amount'] == budget_per_citizen - expected_accrued
    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('10')
def test_send_transaction_after_fruition_period():
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

    transaction = custom_transaction(pan, amount, '2999-01-01T00:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    res = timeline(initiative_id, token)

    assert list(operation['operationType'] for operation in res.json()['operationList']).count('TRANSACTION') == 0

    expected_accrued = 0

    res = wallet(initiative_id, token)

    assert res.json()['amount'] == budget_per_citizen - expected_accrued
    assert res.json()['accrued'] == expected_accrued

    clean_trx_files(curr_file_name)
