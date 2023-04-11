import random
import time
from math import floor

import pytest

from api.idpay import timeline
from api.idpay import wallet
from conf.configuration import secrets
from conf.configuration import settings
from util.dataset_utility import fake_fc
from util.dataset_utility import fake_iban
from util.dataset_utility import fake_pan
from util.transaction_upload import encrypt_and_upload
from util.utility import card_enroll
from util.utility import clean_trx_files
from util.utility import custom_transaction
from util.utility import expect_wallet_counters
from util.utility import get_io_token
from util.utility import iban_enroll
from util.utility import onboard_io
from util.utility import retry_timeline
from util.utility import retry_wallet
from util.utility import transactions_hash

initiative_id = secrets.initiatives.complex.id
cashback_percentage = settings.initiatives.complex.cashback_percentage
budget_per_citizen = settings.initiatives.complex.budget_per_citizen
min_amount = settings.initiatives.complex.min_trx_amount
max_amount = settings.initiatives.complex.max_trx_amount

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses
timeline_operations = settings.IDPAY.endpoints.timeline.operations


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.1')
def test_send_five_transactions_award_second_and_third():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.1.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.1.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.1.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.1.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.1.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.1.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(5000)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.1.7
    assert res.status_code == 201

    # 2.1.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.1.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(30000)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.1.11
    assert res.status_code == 201

    # 2.1.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 2.1.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(45500)
    amount4 = floor(10000)
    transaction3 = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction4 = custom_transaction(pan, amount4, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction3, transaction4])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.1.15
    assert res.status_code == 201

    # 2.1.15
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 2.1.16
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.2')
def test_send_five_transactions_award_second_and_third_not_erode():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.2.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.2.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.2.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(500)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.2.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.2.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.2.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(100)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.2.7
    assert res.status_code == 201

    # 2.2.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.2.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(1000)
    transaction = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.2.11
    assert res.status_code == 201

    # 2.2.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 2.2.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount5 = floor(10000)
    amount6 = floor(15000)
    transaction3 = custom_transaction(pan, amount5, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction4 = custom_transaction(pan, amount6, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction3, transaction4])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.2.15
    assert res.status_code == 201

    # 2.2.15
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 2.2.16
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.3')
def test_send_one_transactions_no_award():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.3.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.3.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.3.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.3.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.3.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.3.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.4')
def test_send_five_transactions_award_decimal():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.4.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.4.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.4.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1055)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.4.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.4.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.4.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(1165)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.4.7
    assert res.status_code == 201

    # 2.4.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.4.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(515)
    transaction = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.4.11
    assert res.status_code == 201

    # 2.4.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 2.4.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.5')
def test_erode_budget_with_one_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.5.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.5.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.5.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(10000)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.5.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.5.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.5.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(10000)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.5.7
    assert res.status_code == 201

    # 2.5.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.5.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(2000)
    transaction = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.5.11
    assert res.status_code == 201

    # 2.5.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 2.5.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.6')
def test_no_award_insufficient_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.6.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.6.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.6.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(199)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.6.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.6.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.6.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(min_amount * 100 - 1)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.6.7
    assert res.status_code == 201

    # 2.6.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.6.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(125)
    amount4 = floor(123)
    transaction3 = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction4 = custom_transaction(pan, amount4, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction3, transaction4])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.6.10
    assert res.status_code == 201

    # 2.6.10
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount3 + amount4) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.6.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.7')
def test_award_max_budget():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.7.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.7.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.7.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(112595)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.7.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.7.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.7.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(200000)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.7.7
    assert res.status_code == 201

    # 2.7.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.7.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.8')
def test_no_award_insufficient_amount_and_transactions():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.8.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.8.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.8.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(50)
    amount2 = floor(55)
    transaction1 = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction2 = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction1), transaction1, transaction2])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.8.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.8.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.8.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(9950)
    transaction3 = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction3), transaction3])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.8.7
    assert res.status_code == 201

    # 2.8.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.8.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.9')
def test_no_reward_on_first_transaction_insufficient_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.9.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.9.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.9.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(99)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.9.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.9.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.9.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(200)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.9.7
    assert res.status_code == 201

    # 2.9.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.9.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(500)
    transaction = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.9.10
    assert res.status_code == 201

    # 2.9.10
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount3 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.9.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.10')
def test_no_reward_on_first_transaction_insufficient_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.10.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.10.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.10.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(20000)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.10.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.10.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.10.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(10010)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.10.7
    assert res.status_code == 201

    # 2.10.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.10.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(50000)
    transaction = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.10.11
    assert res.status_code == 201

    # 2.10.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.10.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount4 = floor(10000)
    amount5 = floor(10000)
    transaction4 = custom_transaction(pan, amount4, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction5 = custom_transaction(pan, amount5, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction4, transaction5])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.6.10
    assert res.status_code == 201

    # 2.6.10
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.10.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.11')
def test_no_reward_one_cent():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.11.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.11.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 2.11.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(551)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.11.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.11.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.11.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(555)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.11.7
    assert res.status_code == 201

    # 2.11.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.11.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(1)
    transaction = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.11.11
    assert res.status_code == 201

    # 2.11.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.11.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)
