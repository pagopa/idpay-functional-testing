import random
import time
from dataclasses import dataclass
from math import floor

import pytest

from api.idpay import timeline
from api.idpay import wallet
from api.issuer import enroll
from conf.configuration import secrets
from conf.configuration import settings
from util.certs_loader import load_pm_public_key
from util.dataset_utility import fake_fc
from util.dataset_utility import fake_iban
from util.dataset_utility import fake_pan
from util.dataset_utility import get_random_time
from util.encrypt_utilities import pgp_string_routine
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

initiative_id = secrets.initiatives.timeframes.id
flat_cashback_amount = settings.initiatives.timeframes.flat_cashback_amount
budget_per_citizen = settings.initiatives.timeframes.budget_per_citizen
min_amount = settings.initiatives.timeframes.min_trx_amount
max_amount = settings.initiatives.timeframes.max_trx_amount
max_daily_amount = settings.initiatives.timeframes.daily_budget

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses
timeline_operations = settings.IDPAY.endpoints.timeline.operations


@dataclass
class Timeframe:
    """Class for keeping track of timeframes."""
    trx_date: str
    start_time: str
    end_time: str


awardable_timeframes = {
    'monday': Timeframe('2099-01-05', '07:00:00', '09:00:00'),
    'tuesday': Timeframe('2099-01-06', '10:00:00', '11:00:00'),
    'wednesday': Timeframe('2099-01-07', '12:00:00', '13:01:00'),
    'thursday': Timeframe('2099-01-08', '13:03:00', '16:59:00'),
    'friday_early': Timeframe('2099-01-08', '23:01:00', '23:59:59'),
    'friday': Timeframe('2099-01-09', '00:00:00', '22:59:59'),
    'saturday_early': Timeframe('2099-01-09', '23:00:00', '23:59:59'),
    'saturday': Timeframe('2099-01-10', '00:00:00', '23:59:59'),
    'sunday': Timeframe('2099-01-11', '00:00:00', '23:59:59'),
}

samples_of_not_awardable_timeframes = {
    'saturday_early': Timeframe('2099-01-09', '23:00:00', '23:59:59'),
    'saturday': Timeframe('2099-01-10', '00:00:00', '23:59:59'),
    'sunday': Timeframe('2099-01-11', '00:00:00', '23:59:59'),
}


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.1')
def test_award_transaction():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.1.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.1.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.1.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(1000)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T07:01:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.1.4
    assert res.status_code == 201

    # 3.1.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.1.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.2')
def test_not_award_transaction_after_allowed_timeframe():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.2.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.2.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.2.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(2500)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T08:59:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.2.4
    assert res.status_code == 201

    # 3.2.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.2.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount = floor(1500)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T09:01:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.2.8
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.2.8
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.2.9
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
def test_award_transaction_exact_timeframe_start():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(2500)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T07:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
def test_award_transaction_exact_timeframe_end():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(2500)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T09:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
def test_not_award_transaction_1ms_before_timeframe():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(2500)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T06:59:59.999Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.2.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.3.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.3.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
def test_not_award_transaction_1ms_after_timeframe():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(2500)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T09:00:00.001Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.3')
def test_not_award_transaction_insufficient_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.3.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.3.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.3.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(400)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T08:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.3.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.3.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction not received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.3.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.4')
def test_award_transaction_1_sec_before_timeframe_end():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.4.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.4.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.4.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(2200)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['tuesday'].trx_date + 'T10:59:59.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.4.4
    assert res.status_code == 201

    # 3.4.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.4.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.5')
def test_not_award_transaction_1_sec_before_timeframe_start():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.5.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.5.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.5.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(3000)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['wednesday'].trx_date + 'T11:59:59.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.5.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.5.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.5.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.6')
def test_not_award_transaction_1_sec_after_timeframe_start():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.6.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.6.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.6.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(4500)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['thursday'].trx_date + 'T18:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.6.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.6.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.6.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.7')
def test_not_award_transaction_exceeds_max_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.7.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.7.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.7.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(450000)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T08:30:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.7.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.7.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.7.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.8')
def test_not_award_transaction_wrong_day():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.8.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.8.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.8.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(5500)
    transaction = custom_transaction(pan=pan, amount=amount1, curr_date=awardable_timeframes['friday'].trx_date
                                                                        + 'T05:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.8.4
    assert res.status_code == 201

    # 3.8.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.8.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount2 = floor(6500)
    transaction = custom_transaction(pan=pan, amount=amount2, curr_date=awardable_timeframes['saturday'].trx_date
                                                                        + 'T09:01:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.8.8
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.8.8
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.8.9
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.9')
def test_not_award_insufficient_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.9.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.9.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.9.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(min_amount - 1)
    transaction = custom_transaction(pan=pan, amount=amount1, curr_date=awardable_timeframes['monday'].trx_date
                                                                        + 'T08:30:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.9.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.9.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.9.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.10')
def test_not_award_exceeds_max_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.10.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.10.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.10.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(max_amount + 1)
    transaction = custom_transaction(pan=pan, amount=amount1, curr_date=awardable_timeframes['tuesday'].trx_date
                                                                        + 'T10:30:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.10.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.10.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.10.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.11')
def test_erode_budget():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.11.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.11.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.11.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    num_transactions_a = 5
    transactions_a = []
    for i in range(num_transactions_a):
        amount = floor(random.randint(min_amount, floor(max_daily_amount / num_transactions_a)))
        curr_date = f'{awardable_timeframes["monday"].trx_date}T{get_random_time("07:00:00", "09:00:00")}.000Z'
        transactions_a.append(custom_transaction(pan=pan, amount=amount, curr_date=curr_date))
    trx_file_content_a = '\n'.join(transactions_a)
    trx_file_content_a_complete = '\n'.join([transactions_hash(trx_file_content_a), trx_file_content_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content_a_complete)

    # 3.11.4
    assert res.status_code == 201

    # 3.11.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=num_transactions_a,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transactions not received')

    expected_accrued = round(float(flat_cashback_amount * num_transactions_a), 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.11.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    num_transactions_b = 6
    transactions_b = []
    for i in range(num_transactions_b):
        amount = floor(random.randint(min_amount, floor(max_daily_amount / num_transactions_b)))
        curr_date = f'{awardable_timeframes["wednesday"].trx_date}T{get_random_time("12:00:00", "13:01:00")}.000Z'
        transactions_b.append(custom_transaction(pan=pan, amount=amount, curr_date=curr_date))
    trx_file_content_b = '\n'.join(transactions_b)
    trx_file_content_b_complete = '\n'.join([transactions_hash(trx_file_content_b), trx_file_content_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content_b_complete)

    # 3.11.9
    assert res.status_code == 201

    # 3.11.9
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=10, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=1,
                   message='Transactions not received')

    # 3.11.9
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=num_transactions_a + num_transactions_b - 10, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=1,
                   message='Transactions not received', page=1)

    expected_accrued = round(float(flat_cashback_amount * (num_transactions_a + num_transactions_b)), 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.11.10
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    num_transactions_c = 8
    transactions_c = []
    for i in range(num_transactions_c):
        amount = floor(random.randint(min_amount, floor(max_daily_amount / num_transactions_c)))
        curr_date = f'{awardable_timeframes["thursday"].trx_date}T{get_random_time("13:0:00", "16:59:00")}.000Z'
        transactions_c.append(custom_transaction(pan=pan, amount=amount, curr_date=curr_date))
    trx_file_content_c = '\n'.join(transactions_c)
    trx_file_content_c_complete = '\n'.join([transactions_hash(trx_file_content_c), trx_file_content_c])
    res, curr_file_name = encrypt_and_upload(trx_file_content_c_complete)

    # 3.11.14
    assert res.status_code == 201

    # 3.11.14
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=10, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=1,
                   message='Transactions not received')

    # 3.11.14
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=num_transactions_a + num_transactions_b + num_transactions_c - 10, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=1,
                   message='Transactions not received', page=1)

    expected_accrued = round(
        float(flat_cashback_amount * (num_transactions_a + num_transactions_b + num_transactions_c)), 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.11.15
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    amount = floor(1000)
    transaction = custom_transaction(pan=pan, amount=amount,
                                     curr_date=awardable_timeframes['friday'].trx_date + 'T16:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.11.19
    assert res.status_code == 201

    # 3.11.19
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=10, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=1,
                   message='Transactions not received')

    # 3.11.19
    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=num_transactions_a + num_transactions_b + num_transactions_c + 1 - 10, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=1,
                   message='Transactions not received', page=1)

    expected_accrued = budget_per_citizen
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.11.20
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.12')
def test_not_award_out_of_amount_range():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 3.12.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.12.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.12.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount1 = floor(1400)
    transaction = custom_transaction(pan=pan, amount=amount1,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T08:30:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.12.4
    assert res.status_code == 201

    # 3.12.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=20, delay=1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.12.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    num_transactions_a = 500
    transactions_a = []
    for i in range(num_transactions_a):
        amount = floor(random.randint(0, min_amount - 1))
        if not not random.getrandbits(1):
            amount = floor(random.randint(max_amount + 1, 99999999))
        curr_date = random.choice(list(awardable_timeframes.items()))[1]
        curr_date_time = f'{curr_date.trx_date}T{get_random_time(curr_date.start_time, curr_date.end_time)}.000Z'
        transactions_a.append(custom_transaction(pan=pan, amount=amount, curr_date=curr_date_time))
    trx_file_content_a = '\n'.join(transactions_a)
    trx_file_content_a_complete = '\n'.join([transactions_hash(trx_file_content_a), trx_file_content_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content_a_complete)

    # 3.12.8
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 3.12.8
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.2,
                   message='Transactions received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.12.9
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.card_removal
@pytest.mark.timeframes
@pytest.mark.use_case('3.13')
def test_no_award_transaction_after_card_removal():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan_a = fake_pan()
    pan_b = fake_pan()
    token = get_io_token(test_fc)

    # 3.13.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.13.2
    card_enroll(test_fc, pan_a, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.13.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount_a = floor(1400)
    transaction = custom_transaction(pan=pan_a, amount=amount_a,
                                     curr_date=awardable_timeframes['tuesday'].trx_date + 'T10:20:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.13.4
    assert res.status_code == 201

    # 3.13.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.13.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    # 3.13.9
    card_removal(test_fc, initiative_id)

    # 3.13.10
    card_enroll(test_fc, pan_b, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    amount_b = floor(5400)
    transaction = custom_transaction(pan=pan_b, amount=amount_b,
                                     curr_date=awardable_timeframes['tuesday'].trx_date + 'T17:30:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.13.11
    assert res.status_code == 201

    # 3.13.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.13.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.14')
def test_ko_card_enroll_already_associated_to_the_same_initiative():
    test_fc_x = fake_fc()
    test_fc_y = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token_x = get_io_token(test_fc_x)
    token_y = get_io_token(test_fc_y)

    # 3.14.1
    onboard_io(test_fc_x, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.14.2
    card_enroll(test_fc_x, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.14.3
    iban_enroll(test_fc_x, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount_a = floor(1400)
    transaction = custom_transaction(pan=pan, amount=amount_a,
                                     curr_date=awardable_timeframes['wednesday'].trx_date + 'T12:20:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.14.4
    assert res.status_code == 201

    # 3.14.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token_x,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.14.4
    expect_wallet_counters(expected_amount_left, expected_accrued, token_x, initiative_id)

    clean_trx_files(curr_file_name)

    # 3.14.5
    onboard_io(test_fc_y, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_y,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    res = enroll(initiative_id,
                 test_fc_y,
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

    assert res.status_code == 403
    assert res.json()['message'] == 'Payment instrument already associated to another citizen'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.15')
def test_ko_card_enroll_already_associated_to_another_initiative():
    test_fc_x = fake_fc()
    test_fc_y = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token_x = get_io_token(test_fc_x)
    token_y = get_io_token(test_fc_y)
    cashback_initiative_id = secrets.initiatives.cashback_like.id

    # 3.15.1
    onboard_io(test_fc_x, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')
    # 3.15.2
    card_enroll(test_fc_x, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.15.3
    iban_enroll(test_fc_x, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount_a = floor(5000)
    transaction = custom_transaction(pan=pan, amount=amount_a,
                                     curr_date=awardable_timeframes['thursday'].trx_date + 'T15:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.15.4
    assert res.status_code == 201

    # 3.15.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token_x,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.15.4
    expect_wallet_counters(expected_amount_left, expected_accrued, token_x, initiative_id)

    clean_trx_files(curr_file_name)

    # 3.15.5
    onboard_io(test_fc_y, cashback_initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_y,
                 initiative_id=cashback_initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    res = enroll(cashback_initiative_id,
                 test_fc_y,
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

    assert res.status_code == 403
    assert res.json()['message'] == 'Payment instrument already associated to another citizen'


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.16')
def test_enroll_same_iban_1():
    test_fc_x = fake_fc()
    test_fc_y = fake_fc()
    test_fc_z = fake_fc()
    iban_1 = fake_iban('00000')
    pan_x = fake_pan()
    pan_y = fake_pan()
    pan_z = fake_pan()
    token_x = get_io_token(test_fc_x)
    token_y = get_io_token(test_fc_y)
    token_z = get_io_token(test_fc_z)

    # 3.16.1
    onboard_io(test_fc_x, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    # 3.16.2
    card_enroll(test_fc_x, pan_x, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.16.3
    iban_enroll(test_fc_x, iban_1, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    # 3.16.5
    onboard_io(test_fc_y, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_y,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    # 3.16.6
    card_enroll(test_fc_y, pan_y, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_y,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.16.8
    iban_enroll(test_fc_y, iban_1, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_y,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    # 3.16.9
    onboard_io(test_fc_z, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_z,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.2,
                 message='Not subscribed')

    # 3.16.10
    card_enroll(test_fc_z, pan_z, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_z,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.16.12
    iban_enroll(test_fc_z, iban_1, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_z,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(5000)
    transaction = custom_transaction(pan=pan_x, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T07:30:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.16.13
    assert res.status_code == 201

    # 3.16.13
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token_x,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.16.14
    expect_wallet_counters(expected_amount_left, expected_accrued, token_x, initiative_id)

    clean_trx_files(curr_file_name)

    amount = floor(2000)
    transaction = custom_transaction(pan=pan_y, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T08:20:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.16.17
    assert res.status_code == 201

    # 3.16.17
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token_y,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.16.18
    expect_wallet_counters(expected_amount_left, expected_accrued, token_y, initiative_id)

    clean_trx_files(curr_file_name)

    amount = floor(3000)
    transaction = custom_transaction(pan=pan_z, amount=amount,
                                     curr_date=awardable_timeframes['monday'].trx_date + 'T08:45:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.16.21
    assert res.status_code == 201

    # 3.16.21
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token_z,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.16.22
    expect_wallet_counters(expected_amount_left, expected_accrued, token_z, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.timeframes
@pytest.mark.use_case('3.17')
def test_enroll_same_iban_2():
    test_fc_x = fake_fc()
    test_fc_y = fake_fc()
    test_fc_z = fake_fc()
    curr_iban_xy = fake_iban('00000')
    pan_x = fake_pan()
    pan_y = fake_pan()
    pan_z = fake_pan()
    token_x = get_io_token(test_fc_x)
    token_y = get_io_token(test_fc_y)
    token_z = get_io_token(test_fc_z)

    # 3.17.1
    onboard_io(test_fc_x, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    # 3.17.2
    onboard_io(test_fc_y, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_y,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Not subscribed')

    # 3.17.3
    card_enroll(test_fc_x, pan_x, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.17.4
    card_enroll(test_fc_y, pan_y, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_y,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.17.5
    iban_enroll(test_fc_x, curr_iban_xy, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_x,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    # 3.17.6
    iban_enroll(test_fc_y, curr_iban_xy, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_y,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    # 3.17.7
    onboard_io(test_fc_z, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_z,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.2,
                 message='Not subscribed')

    # 3.17.8
    card_enroll(test_fc_z, pan_z, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_z,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='Card not enrolled')

    # 3.17.9
    iban_enroll(test_fc_z, curr_iban_xy, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_z,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1,
                 message='IBAN not enrolled')

    amount = floor(5000)
    transaction = custom_transaction(pan=pan_z, amount=amount,
                                     curr_date=awardable_timeframes['thursday'].trx_date + 'T15:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 3.17.11
    assert res.status_code == 201

    # 3.17.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token_z,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = flat_cashback_amount
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 3.17.15
    expect_wallet_counters(expected_amount_left, expected_accrued, token_z, initiative_id)

    clean_trx_files(curr_file_name)
