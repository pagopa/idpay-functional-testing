import random
import time
from math import floor

import pytest
from idpay import timeline
from idpay import wallet

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
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Not subscribed')
    # 2.1.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
                 message='Card not enrolled')

    # 2.1.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3,
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
                   initiative_id=initiative_id, field='operationType', tries=1, delay=1,
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
