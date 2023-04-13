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
from util.utility import card_removal
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


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.12')
def test_no_reward_zero_cent():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.12.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.12.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.12.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(0)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.12.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.12.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.12.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(10000)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.12.7
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.12.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.12.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.use_case('2.13')
def test_no_reward_exceed_max_trx_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.13.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.13.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.13.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(max_amount * 100 + 1)
    transaction = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.13.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.13.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.13.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(max_amount * 100 + 5)
    transaction = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.13.7
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.13.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.13.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(3000)
    transaction = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.13.10
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.13.10
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.13.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount4 = floor(2000)
    transaction = custom_transaction(pan, amount4, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.13.13
    assert res.status_code == 201

    # 2.13.13
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount4 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.13.14
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount5 = floor(2500)
    transaction = custom_transaction(pan, amount5, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.13.17
    assert res.status_code == 201

    # 2.13.17
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount4 + amount5) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.13.18
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.14')
def test_wrong_reward_reverting_first_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.14.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.14.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.14.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction_a = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.14.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.14.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.14.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(2000)
    transaction_b = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.14.7
    assert res.status_code == 201

    # 2.14.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.14.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(amount1)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True,
                                                mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.14.11
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.14.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    # 2.14.11
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=0,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.14.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount4 = floor(1000)
    transaction = custom_transaction(pan, amount4, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.14.12
    assert res.status_code == 201

    # 2.14.12
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount4) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.14.13
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.15')
def test_no_reward_on_reverted_not_awarded_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.15.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.15.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.15.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction_a = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.15.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.15.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.15.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(2000)
    transaction_b = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.15.7
    assert res.status_code == 201

    # 2.15.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.15.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(2000)
    transaction_c = custom_transaction(pan=pan, amount=amount3,
                                       mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_c), transaction_c])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.15.11
    assert res.status_code == 201

    # 2.15.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.15.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount4 = floor(5000)
    transaction_d = custom_transaction(pan=pan, amount=amount4,
                                       mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_d), transaction_d])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.15.16
    assert res.status_code == 201

    # 2.15.16
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.15.17
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(amount1)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True,
                                                mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.15.19
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.15.19
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    # 2.15.19
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=0,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.15.18
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.16')
def test_update_reward_on_reverted_awarded_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.16.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.16.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.16.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction_a = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.16.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.16.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.16.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(2000)
    transaction_b = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_b_correlation_id = transaction_b.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.16.7
    assert res.status_code == 201

    # 2.16.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.16.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(amount2)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_b_correlation_id,
                                                reversal=True,
                                                mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.16.12
    assert res.status_code == 201

    # 2.16.12
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.16.13
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(3000)
    transaction_c = custom_transaction(pan=pan, amount=amount3,
                                       mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_c), transaction_c])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.16.14
    assert res.status_code == 201

    # 2.16.14
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount3 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.16.15
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(amount1)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True,
                                                mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.16.19
    assert res.status_code == 201

    # 2.16.19
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal not received')

    # 2.16.19
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount3 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.16.21
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.17')
def test_partial_reversal_on_first_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.17.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.17.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.17.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction_a = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.17.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.17.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.17.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(1522)
    transaction_b = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.17.7
    assert res.status_code == 201

    # 2.17.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.17.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(1211)
    transaction_c = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_c), transaction_c])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.17.12
    assert res.status_code == 201

    # 2.17.12
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.17.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(500)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True,
                                                mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.17.17
    assert res.status_code == 201

    # 2.17.17
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=0,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal not received')

    # 2.17.17
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.17.18
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.18')
def test_partial_reversal_on_firts_transaction_making_it_unacceptable():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.18.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.18.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.18.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(200)
    transaction_a = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.18.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.18.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.18.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(1522)
    transaction_b = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.18.7
    assert res.status_code == 201

    # 2.18.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.18.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(1211)
    transaction_c = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_c), transaction_c])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.18.12
    assert res.status_code == 201

    # 2.18.12
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.18.13
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(150)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True,
                                                mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.18.17
    assert res.status_code == 201

    # 2.18.17
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=0,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal not received')

    # 2.18.17
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.18.18
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.19')
def test_no_award_new_transaction_after_reversal_on_first_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.19.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.19.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.19.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction_a = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.19.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.19.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.19.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(2000)
    transaction_b = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.19.7
    assert res.status_code == 201

    # 2.19.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.19.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(amount1)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True,
                                                mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.19.12
    assert res.status_code == 201

    # 2.19.12
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=0,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal not received')

    # 2.19.12
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.19.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(1000)
    transaction_c = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_c), transaction_c])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.19.13
    assert res.status_code == 201

    # 2.19.13
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.19.14
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    amount4 = floor(5000)
    transaction_d = custom_transaction(pan, amount4, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_d), transaction_d])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.19.18
    assert res.status_code == 201

    # 2.19.18
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.19.23
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.20')
def test_award_new_transaction_after_reversal_on_awarded_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.20.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.20.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.20.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction_a = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.20.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.20.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.20.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(3000)
    transaction_b = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.20.7
    assert res.status_code == 201

    # 2.20.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.20.11
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount3 = floor(2000)
    transaction_c = custom_transaction(pan, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_c), transaction_c])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.20.13
    assert res.status_code == 201

    # 2.20.13
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.20.14
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(amount1)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True,
                                                mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.20.12
    assert res.status_code == 201

    # 2.20.12
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=0,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal not received')

    # 2.20.12
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.20.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount4 = floor(4000)
    transaction_d = custom_transaction(pan, amount4, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_d), transaction_d])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.20.18
    assert res.status_code == 201

    # 2.20.18
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3 + amount4) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.20.23
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.21')
def test_no_award_wrong_mcc():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.21.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.21.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.21.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1000)
    transaction_a = custom_transaction(pan, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.21.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.21.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.21.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(5000)
    wrong_mcc = str(random.randint(1, 9999)).zfill(4)
    while wrong_mcc in settings.initiatives.complex.mcc_whitelist:
        wrong_mcc = str(random.randint(1, 9999)).zfill(4)

    transaction_b = custom_transaction(pan, amount2, mcc=wrong_mcc)
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.21.7
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.21.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.21.10
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.22')
def test_no_award_wrong_mcc_on_first_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 2.22.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.22.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.22.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(3000)
    wrong_mcc = str(random.randint(1, 9999)).zfill(4)
    while wrong_mcc in settings.initiatives.complex.mcc_whitelist:
        wrong_mcc = str(random.randint(1, 9999)).zfill(4)
    transaction_a = custom_transaction(pan, amount1, mcc=wrong_mcc)
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.22.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.22.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.22.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(2000)
    transaction_b = custom_transaction(pan, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.22.7
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.22.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.22.10
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.complex
@pytest.mark.reversal
@pytest.mark.use_case('2.25')
def test_award_transactions_done_with_two_payment_methods():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan1 = fake_pan()
    pan2 = fake_pan()
    token = get_io_token(test_fc)

    # 2.25.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 2.25.2
    card_enroll(test_fc, pan1, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5,
                 message='Card not enrolled')

    # 2.25.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(3000)
    transaction_a = custom_transaction(pan1, amount1, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.25.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.25.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.25.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(5000)
    transaction_b = custom_transaction(pan1, amount2, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.25.7
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 2.25.7
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.25.10
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    # 2.25.11
    card_removal(test_fc, initiative_id)

    # 2.25.12
    card_enroll(test_fc, pan2, initiative_id)
    retry_timeline(expected=timeline_operations.add_instrument, request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', num_required=2, tries=50,
                   delay=0.5, message='Card not enrolled')

    amount3 = floor(2000)
    transaction_c = custom_transaction(pan2, amount3, mcc=random.choice(settings.initiatives.complex.mcc_whitelist))
    trx_file_content = '\n'.join([transactions_hash(transaction_c), transaction_c])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 2.25.13
    assert res.status_code == 201

    # 2.25.13
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor((amount2 + amount3) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 2.25.7
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)
