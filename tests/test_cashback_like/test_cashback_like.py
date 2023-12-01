import datetime
import random
import time
from math import floor

import pytest

from api.idpay import enroll_iban
from api.idpay import get_initiative_statistics
from api.idpay import get_payment_instruments
from api.idpay import timeline
from api.idpay import unsubscribe
from api.idpay import wallet
from api.issuer import enroll
from api.onboarding_io import accept_terms_and_conditions
from conf.configuration import secrets
from conf.configuration import settings
from util.certs_loader import load_pm_public_key
from util.dataset_utility import fake_fc
from util.dataset_utility import fake_iban
from util.dataset_utility import fake_pan
from util.dataset_utility import Reward
from util.encrypt_utilities import pgp_string_routine
from util.transaction_upload import encrypt_and_upload
from util.utility import card_enroll
from util.utility import card_removal
from util.utility import check_rewards
from util.utility import check_statistics
from util.utility import clean_trx_files
from util.utility import custom_transaction
from util.utility import expect_wallet_counters
from util.utility import get_io_token
from util.utility import iban_enroll
from util.utility import onboard_io
from util.utility import retry_timeline
from util.utility import retry_wallet
from util.utility import transactions_hash

organization_id = secrets.organization_id
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
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.2.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.2.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.2.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

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

    # 1.2.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.2.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)
    # 1.2.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.3')
def test_send_50_transaction_erode_budget_max_award():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    num_trx = 50
    min_amount = 340.833885
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.3.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.3.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.3.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    transactions = []
    for i in range(num_trx):
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
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.3.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     skip_trx_check=True)

    # 1.3.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.4')
def test_send_single_200e_transaction_erode_budget_max_award():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.4.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.4.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.4.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

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
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.4.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.5')
def test_not_award_after_budget_erosion():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.5.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.5.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.5.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

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
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    # 1.5.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=2)

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
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.reversal
@pytest.mark.use_case('1.6')
def test_award_again_after_reversal():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    curr_amount = floor(3408.33885)
    num_trx = 5
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.6.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.6.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.6.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

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
                   initiative_id=initiative_id, field='operationType', tries=20, delay=3,
                   message='Transaction not received')

    expected_accrued = budget_per_citizen
    expected_amount_left = 0
    # 1.6.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.6.6
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=num_trx)

    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

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
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.6.9
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)

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
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.6.12
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, 0 - expected_reversal)])
    # 1.6.12
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=num_trx - 1)

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

    least_accrued = round(floor(amount * cashback_percentage) / 10000, 2)
    expected_accrued = round(budget_per_citizen - expected_reversal + least_accrued, 2)
    expected_amount_left = round(budget_per_citizen - expected_accrued, 2)
    # 1.6.14
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.6.15
    check_rewards(initiative_id=initiative_id,
                  expected_rewards=[Reward(curr_iban, least_accrued)])

    # 1.6.16
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=num_trx)
    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.7')
def test_send_transaction_ko_card_enroll():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.7.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

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
    assert res.status_code == 500
    assert res.json()['code'] == 'WALLET_GENERIC_ERROR'
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
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
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.7.6
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=0,
                     rewarded_trxs_increment=0)

    # 1.7.7
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.card_removal
@pytest.mark.use_case('1.8')
def test_remove_card_and_enroll_again():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.8.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.8.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.8.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount1 = floor(random.random() * max_amount)
    transaction = custom_transaction(pan, amount1)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.8.4
    assert res.status_code == 201
    # 1.8.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = round(floor(amount1 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.8.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.8.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    # 1.8.7
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    clean_trx_files(curr_file_name)

    time.sleep(random.randint(10, 15))

    # 1.8.8
    card_removal(test_fc, initiative_id)

    amount2 = 2750
    transaction = custom_transaction(pan, amount2)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.8.9
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 1.8.9
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction received')

    # 1.8.10
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.8.10
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    # 1.8.11
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)
    # 1.8.12
    card_enroll(test_fc, pan, initiative_id, num_required=2)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount3 = 1369
    transaction = custom_transaction(pan, amount3)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.8.13
    assert res.status_code == 201

    # 1.8.13
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    least_accrued = round(floor(amount3 * cashback_percentage) / 10000, 2)
    expected_accrued = budget_per_citizen if round(
        round(floor(amount1 * cashback_percentage) / 10000, 2) + least_accrued, 2) > budget_per_citizen else round(
        round(floor(amount1 * cashback_percentage) / 10000, 2) + round(
            floor(amount3 * cashback_percentage) / 10000, 2), 2)
    expected_amount_left = 0 if round(float(budget_per_citizen - expected_accrued), 2) < 0 else round(
        float(budget_per_citizen - expected_accrued), 2)

    # 1.8.14
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=2)
    # 1.8.14
    expect_wallet_counters(expected_amount=expected_amount_left, expected_accrued=expected_accrued, token=token,
                           initiative_id=initiative_id)
    # 1.8.15
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, least_accrued)])


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.use_case('1.9')
def test_ko_iban_enroll():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.9.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.9.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.9.3
    res = enroll_iban(initiative_id,
                      token,
                      {
                          'iban': '',
                          'description': 'TEST Bank account'
                      }
                      )
    assert res.status_code == 400
    assert res.json()['code'] == 'WALLET_INVALID_REQUEST'

    time.sleep(random.randint(10, 15))

    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    retry_timeline(expected=timeline_operations.add_iban, request=timeline, token=token,
                   initiative_id=initiative_id, field='operationType', num_required=0, tries=3, delay=3,
                   message='IBAN not enrolled')

    amount = floor(random.random() * max_amount)

    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.9.4
    assert res.status_code == 201

    # 1.9.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.9.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.9.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    # 1.9.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)

    clean_trx_files(curr_file_name)

    # 1.9.7
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.9.7
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('1.10')
def test_small_amount_no_award():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.10.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.10.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.10.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount = 1
    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.10.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 1.10.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.10.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.10.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=0)

    # 1.10.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('1.11')
def test_send_minimum_awardable_amount():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.11.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.11.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.11.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount = floor(random.randint(2, 4))
    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.11.4
    assert res.status_code == 201
    # 1.11.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.11.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.11.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    # 1.11.7
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.reward
@pytest.mark.use_case('1.12')
def test_send_transaction_after_fruition_period():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.12.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.12.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.12.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount = floor(random.random() * max_amount)
    transaction = custom_transaction(pan=pan, amount=amount, curr_date='2099-03-13T23:00:00.000Z')
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.12.5
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 1.12.5
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.12.6
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.12.6
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=0)

    # 1.12.7
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.use_case('1.14')
def test_correct_statistic_of_onboard_citizen():
    num_onboards = random.randint(5, 10)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    for i in range(num_onboards):
        test_fc = fake_fc()
        curr_iban = fake_iban('00000')
        pan = fake_pan()
        token = get_io_token(test_fc)

        # 1.14.1
        onboard_io(test_fc, initiative_id).json()
        retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                     initiative_id=initiative_id, field='status', tries=3, delay=3)

        # 1.14.2
        card_enroll(test_fc, pan, initiative_id)
        retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                     initiative_id=initiative_id, field='status', tries=3, delay=3)

        # 1.14.3
        iban_enroll(test_fc, curr_iban, initiative_id)
        retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                     initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.14.4
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=num_onboards, accrued_rewards_increment=0,
                     rewarded_trxs_increment=0)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.unsubscribe
@pytest.mark.reward
@pytest.mark.use_case('1.22')
def test_send_transaction_after_unsubscribe():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.22.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.22.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.22.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    res = unsubscribe(initiative_id, token)
    # 1.22.4
    assert res.status_code == 204
    # 1.22.4
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.22.6
    assert [] == get_payment_instruments(initiative_id=initiative_id, token=token).json()['instrumentList']

    # Send the transaction
    amount = floor(1000)
    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])

    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.22.7
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.22.7
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=0)

    # 1.22.8
    expect_wallet_counters(expected_amount_left, expected_accrued, token=token, initiative_id=initiative_id)

    # 1.22.8
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.enroll
@pytest.mark.onboard
@pytest.mark.unsubscribe
@pytest.mark.reward
@pytest.mark.use_case('1.24')
def test_onboarding_after_unsubscribe():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 1.24.0
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.24.0
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.24.0
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    res = unsubscribe(initiative_id, token)
    # 1.24.0
    assert res.status_code == 204
    # 1.24.0
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.24.0
    assert [] == get_payment_instruments(initiative_id=initiative_id, token=token).json()['instrumentList']

    # 1.24.1
    res = accept_terms_and_conditions(token, initiative_id)
    assert res.status_code == 403
    assert res.json()['code'] == 'ONBOARDING_USER_UNSUBSCRIBED'
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    res = enroll(initiative_id,
                 test_fc,
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
    # 1.24.2
    assert res.status_code == 403
    assert res.json()['code'] == 'WALLET_USER_UNSUBSCRIBED'
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.unsubscribe
@pytest.mark.cashback
@pytest.mark.use_case('1.25')
def test_get_pending_reward_after_unsubscribe():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.25.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.25.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.25.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount = floor(random.random() * max_amount)
    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.25.4
    assert res.status_code == 201
    # 1.25.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.25.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.25.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    res = unsubscribe(initiative_id, token)
    # 1.25.6
    assert res.status_code == 204
    # 1.25.6
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.25.7
    assert [] == get_payment_instruments(initiative_id=initiative_id, token=token).json()['instrumentList']

    # 1.25.8
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.unsubscribe
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.use_case('1.28')
def test_onboarding_after_unsubscribe():
    test_fc_a = fake_fc()
    test_fc_b = fake_fc()
    curr_iban = fake_iban('00000')
    pan_a = fake_pan()
    pan_b = fake_pan()
    token_a = get_io_token(test_fc_a)
    token_b = get_io_token(test_fc_b)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.28.1
    onboard_io(test_fc_a, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_a,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.28.2
    card_enroll(test_fc_a, pan_a, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_a,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.28.3
    iban_enroll(test_fc_a, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_a,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.28.4
    onboard_io(test_fc_b, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token_b,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.28.5
    card_enroll(test_fc_b, pan_b, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_b,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.28.6
    iban_enroll(test_fc_b, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_b,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    res = unsubscribe(initiative_id, token_a)
    # 1.28.7
    assert res.status_code == 204
    # 1.28.7
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token_a,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.28.8
    assert [] == get_payment_instruments(initiative_id=initiative_id, token=token_a).json()['instrumentList']

    # 1.28.9
    res = accept_terms_and_conditions(token_a, initiative_id)
    assert res.status_code == 403
    assert res.json()['code'] == 'ONBOARDING_USER_UNSUBSCRIBED'
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token_a,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount = floor(2500)
    transaction = custom_transaction(pan_b, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.28.10
    assert res.status_code == 201
    # 1.28.10
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token_b,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.28.10
    expect_wallet_counters(expected_amount_left, expected_accrued, token_b, initiative_id)

    # 1.28.10
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=2, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    # 1.28.11
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.cashback
@pytest.mark.need_fix
@pytest.mark.use_case('1.27')
def test_homocode_onboarding():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)

    # 1.27.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.27.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.27.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount = floor(random.random() * max_amount)
    transaction = custom_transaction(pan, amount)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.27.4
    assert res.status_code == 201
    # 1.27.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    expected_accrued = round(floor(amount * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.27.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    clean_trx_files(curr_file_name)

    token1 = get_io_token(test_fc)
    res = accept_terms_and_conditions(token1, initiative_id)
    # 1.27.7
    assert res.status_code != 204


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.timing
@pytest.mark.cashback
@pytest.mark.use_case('1.29')
def test_no_reward_transaction_1sec_before_card_enrollment():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.29.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    # 1.29.2
    # Save card enrollment time
    trx_time = (datetime.datetime.utcnow() - datetime.timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    card_enroll(test_fc, pan, initiative_id)

    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    # 1.29.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)

    amount = floor(1000)
    transaction = custom_transaction(pan=pan, amount=amount, curr_date=trx_time)
    trx_file_content = '\n'.join([transactions_hash(transaction), transaction])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.29.4
    assert res.status_code == 201

    time.sleep(random.randint(10, 15))

    # 1.29.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=0, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction received')

    expected_accrued = 0
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)

    # 1.29.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.29.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=0)

    # 1.29.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.reversal
@pytest.mark.cashback
@pytest.mark.use_case('1.31')
def test_award_correct_amount_after_partial_reversal():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.31.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1)
    # 1.31.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5)

    # 1.31.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1)

    amount1 = floor(3500)
    transaction_a = custom_transaction(pan, amount1)
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.31.4
    assert res.status_code == 201

    # 1.31.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount1 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.31.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.31.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    # 1.31.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    clean_trx_files(curr_file_name)

    reverse_amount = floor(500)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True)
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.31.8
    assert res.status_code == 201

    # 1.31.8
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    # 1.31.8
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal received')

    expected_reversal = round(floor(reverse_amount * cashback_percentage) / 10000, 2)
    expected_accrued = expected_accrued - expected_reversal
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.31.9
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.31.10
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    # 1.31.11
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, 0 - expected_reversal)])

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.reversal
@pytest.mark.cashback
@pytest.mark.use_case('1.32')
def test_no_reward_after_complete_reversal():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.32.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1)
    # 1.32.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5)

    # 1.32.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1)

    amount1 = floor(2500)
    transaction_a = custom_transaction(pan, amount1)
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.32.4
    assert res.status_code == 201

    # 1.32.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount1 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.32.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.32.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    clean_trx_files(curr_file_name)

    reverse_amount = floor(amount1)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True)
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.32.6
    assert res.status_code == 201

    # 1.32.6
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    # 1.32.6
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal received')

    expected_accrued = round(floor((amount1 - reverse_amount) * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.32.7
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.32.8
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)],
                  check_absence=True)

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.reversal
@pytest.mark.cashback
@pytest.mark.use_case('1.33')
def test_reward_transaction_after_complete_reversal():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.33.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1)
    # 1.33.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5)

    # 1.33.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1)

    amount1 = floor(1000)
    transaction_a = custom_transaction(pan, amount1)
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.33.4
    assert res.status_code == 201

    # 1.33.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount1 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.33.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.33.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)
    # 1.33.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    clean_trx_files(curr_file_name)

    reverse_amount = floor(amount1)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True)
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.33.8
    assert res.status_code == 201

    # 1.33.8
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    # 1.33.8
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal received')

    expected_reversal = round(floor(reverse_amount * cashback_percentage) / 10000, 2)
    expected_accrued = expected_accrued - expected_reversal
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.33.9
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.33.10
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=0)

    # 1.33.11
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, 0 - expected_reversal)])

    clean_trx_files(curr_file_name)


@pytest.mark.IO
@pytest.mark.onboard
@pytest.mark.enroll
@pytest.mark.reward
@pytest.mark.reversal
@pytest.mark.cashback
@pytest.mark.use_case('1.34')
def test_reward_transaction_after_partial_reversal():
    test_fc = fake_fc()
    curr_iban = fake_iban('00000')
    pan = fake_pan()
    token = get_io_token(test_fc)
    old_statistics = get_initiative_statistics(organization_id=organization_id, initiative_id=initiative_id).json()

    # 1.34.1
    onboard_io(test_fc, initiative_id).json()
    retry_wallet(expected=wallet_statuses.not_refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1)
    # 1.34.2
    card_enroll(test_fc, pan, initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=20, delay=0.5)

    # 1.34.3
    iban_enroll(test_fc, curr_iban, initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=50, delay=0.1)

    amount1 = floor(2500)
    transaction_a = custom_transaction(pan, amount1)
    transaction_a_correlation_id = transaction_a.split(';')[7]
    trx_file_content = '\n'.join([transactions_hash(transaction_a), transaction_a])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.34.4
    assert res.status_code == 201

    # 1.34.4
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    expected_accrued = round(floor(amount1 * cashback_percentage) / 10000, 2)
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.34.5
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.34.5
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)
    # 1.34.6
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, expected_accrued)])

    clean_trx_files(curr_file_name)

    reverse_amount = floor(500)
    transaction_a_reversal = custom_transaction(pan=pan, amount=reverse_amount,
                                                correlation_id=transaction_a_correlation_id,
                                                reversal=True)
    trx_file_content = '\n'.join([transactions_hash(transaction_a_reversal), transaction_a_reversal])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.34.8
    assert res.status_code == 201

    # 1.34.8
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    # 1.34.8
    retry_timeline(expected=timeline_operations.reversal, request=timeline,
                   num_required=1,
                   token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Reversal received')

    expected_reversal = round(floor(reverse_amount * cashback_percentage) / 10000, 2)
    expected_accrued = expected_accrued - expected_reversal
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.34.9
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.34.9
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=1)

    clean_trx_files(curr_file_name)

    amount2 = floor(1000)
    transaction_b = custom_transaction(pan, amount2)
    trx_file_content = '\n'.join([transactions_hash(transaction_b), transaction_b])
    res, curr_file_name = encrypt_and_upload(trx_file_content)
    # 1.34.11
    assert res.status_code == 201

    # 1.34.11
    retry_timeline(expected=timeline_operations.transaction, request=timeline, num_required=2, token=token,
                   initiative_id=initiative_id, field='operationType', tries=50, delay=0.1,
                   message='Transaction not received')

    newly_accrued = round(floor(amount2 * cashback_percentage) / 10000, 2)
    expected_accrued = expected_accrued + newly_accrued
    expected_amount_left = round(float(budget_per_citizen - expected_accrued), 2)
    # 1.34.12
    expect_wallet_counters(expected_amount_left, expected_accrued, token, initiative_id)

    # 1.34.12
    check_statistics(organization_id=organization_id, initiative_id=initiative_id, old_statistics=old_statistics,
                     onboarded_citizen_count_increment=1, accrued_rewards_increment=expected_accrued,
                     rewarded_trxs_increment=2)

    # 1.34.13
    check_rewards(initiative_id=initiative_id, expected_rewards=[Reward(curr_iban, newly_accrued - expected_reversal)])

    clean_trx_files(curr_file_name)
