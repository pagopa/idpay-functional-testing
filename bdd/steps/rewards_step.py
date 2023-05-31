from math import floor

from behave import given
from behave import then

from util.utility import expect_wallet_counters


@then('the citizen is rewarded accordingly')
def step_check_rewards_on_wallet(context):
    step_set_expected_accrued(context=context)
    step_set_expected_amount_left(context=context)
    expect_wallet_counters(context.expected_amount_left, context.expected_accrued, context.token_io,
                           context.initiative_id)


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
