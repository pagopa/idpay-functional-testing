from math import floor

from behave import given
from behave import then

from util.dataset_utility import Reward
from util.utility import check_rewards
from util.utility import expect_wallet_counters
from util.utility import get_io_token


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
