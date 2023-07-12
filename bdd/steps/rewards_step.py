import time
from math import floor

from behave import given
from behave import then
from behave import when

from api.idpay import get_initiative_statistics
from api.idpay import get_initiative_statistics_merchant_portal
from api.idpay import get_transaction_detail
from api.idpay import put_merchant_confirms_payment
from api.idpay import timeline
from conf.configuration import secrets
from util.dataset_utility import Reward
from util.utility import check_merchant_statistics
from util.utility import check_processed_transactions
from util.utility import check_rewards
from util.utility import check_statistics
from util.utility import check_unprocessed_transactions
from util.utility import expect_wallet_counters
from util.utility import get_io_token
from util.utility import retry_timeline


def step_check_rewards_on_wallet(context, token_io):
    step_set_expected_accrued(context=context)
    step_set_expected_amount_left(context=context)
    expect_wallet_counters(context.expected_amount_left, context.expected_accrued, token_io,
                           context.initiative_id)


@then('the citizen {citizen_name} is rewarded accordingly')
def step_check_rewards_of_citizen(context, citizen_name):
    curr_token_io = get_io_token(context.citizens_fc[citizen_name])
    expected_accrued = context.accrued_per_citizen[citizen_name] / 100
    expected_amount_left = (context.initiatives_settings['budget_per_citizen'] * 100 - context.accrued_per_citizen[
        citizen_name]) / 100

    expect_wallet_counters(expected_amount=expected_amount_left, expected_accrued=expected_accrued, token=curr_token_io,
                           initiative_id=context.initiative_id)


@then('the citizen {citizen_name} has its transaction cancelled')
def step_check_transaction_cancellation_on_citizen(context, citizen_name):
    curr_token_io = get_io_token(context.citizens_fc[citizen_name])

    expect_wallet_counters(expected_amount=context.initiatives_settings['budget_per_citizen'], expected_accrued=0,
                           token=curr_token_io,
                           initiative_id=context.initiative_id)

    retry_timeline(expected='CANCELLED',
                   request=timeline,
                   num_required=1,
                   token=curr_token_io,
                   initiative_id=context.initiative_id,
                   field='status',
                   tries=10,
                   delay=3,
                   message='Cancellation not received')


@given('an expected accrued')
def step_set_expected_accrued(context):
    context.cashback_percentage = context.initiatives_settings['cashback_percentage']
    context.budget_per_citizen = context.initiatives_settings['budget_per_citizen']
    if round(floor(context.amount_cents * context.cashback_percentage) / 10000, 2) > context.budget_per_citizen:
        expected_accrued = context.budget_per_citizen
        expected_accrued_cents = floor(context.budget_per_citizen * 100)
    else:
        expected_accrued = round(floor(context.amount_cents * context.cashback_percentage) / 10000, 2)
        expected_accrued_cents = round(floor(context.amount_cents * context.cashback_percentage) / 100, 2)

    context.expected_accrued = expected_accrued
    context.expected_accrued_cents = expected_accrued_cents


@given('an expected amount left')
def step_set_expected_amount_left(context):
    context.expected_amount_left = round(float(context.budget_per_citizen - context.expected_accrued), 2)


@then('the merchant {merchant_name} is refunded {expected_refund} euros')
def step_check_rewards_of_merchant(context, merchant_name, expected_refund):
    curr_iban = context.merchants[merchant_name]['iban']
    check_rewards(initiative_id=context.initiative_id,
                  expected_rewards=[Reward(curr_iban, float(expected_refund))])


@when('the batch process confirms the transaction {trx_name}')
def step_merchant_confirms_a_transactions(context, trx_name):
    curr_merchant_name = context.associated_merchant[trx_name]
    curr_merchant_id = context.merchants[curr_merchant_name]['id']
    context.transactions[trx_name] = get_transaction_detail(context.transactions[trx_name]['id'],
                                                            merchant_id=curr_merchant_id).json()
    assert_merchant_confirmation(trx_id=context.transactions[trx_name]['id'], merchant_id=curr_merchant_id)

    check_statistics(organization_id=context.organization_id,
                     initiative_id=context.initiative_id,
                     old_statistics=context.base_statistics,
                     onboarded_citizen_count_increment=0,
                     accrued_rewards_increment=context.transactions[trx_name]['rewardCents'] / 100,
                     rewarded_trxs_increment=1
                     )
    context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                        initiative_id=context.initiative_id).json()

    check_merchant_statistics(merchant_id=curr_merchant_id,
                              initiative_id=context.initiative_id,
                              old_statistics=context.base_merchants_statistics[curr_merchant_name],
                              accrued_rewards_increment=context.transactions[trx_name]['rewardCents'] / 100
                              )
    context.base_merchants_statistics[curr_merchant_name] = get_initiative_statistics_merchant_portal(
        merchant_id=curr_merchant_id,
        initiative_id=context.initiative_id).json()

    check_processed_transactions(initiative_id=context.initiative_id,
                                 expected_trx_id=context.transactions[trx_name]['id'],
                                 expected_reward=context.transactions[trx_name]['rewardCents'],
                                 expected_fiscal_code=context.associated_citizen[trx_name],
                                 merchant_id=curr_merchant_id
                                 )

    check_unprocessed_transactions(initiative_id=context.initiative_id,
                                   expected_trx_id=context.transactions[trx_name]['id'],
                                   expected_effective_amount=context.transactions[trx_name]['rewardCents'],
                                   expected_reward_amount=context.transactions[trx_name]['rewardCents'],
                                   expected_fiscal_code=context.associated_citizen[trx_name],
                                   merchant_id=curr_merchant_id,
                                   check_absence=True
                                   )


@when('the batch process confirms all the transactions')
def step_merchant_confirms_all_transactions(context):
    for curr_trx_id in context.trx_ids:
        assert_merchant_confirmation(trx_id=curr_trx_id, merchant_id=context.latest_merchant_id)


def assert_merchant_confirmation(trx_id, merchant_id):
    # for testing purposes the transaction is confirmed by the merchant as the batch process would do
    res = put_merchant_confirms_payment(
        transaction_id=trx_id,
        merchant_id=merchant_id
    )
    assert res.status_code == 200
    assert res.json()['status'] == 'REWARDED'
    time.sleep(1)
