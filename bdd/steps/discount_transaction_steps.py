import time
from math import floor

from behave import given
from behave import then
from behave import when

from api.idpay import get_transaction_detail
from api.idpay import post_merchant_create_transaction_acquirer
from api.idpay import put_authorize_payment
from api.idpay import put_pre_authorize_payment
from bdd.steps.rewards_step import step_set_expected_accrued


@when('the merchant tries to generate a transaction of amount {amount_cents} cents')
def step_when_merchant_tries_to_create_a_transaction(context, amount_cents):
    context.create_transaction_response = post_merchant_create_transaction_acquirer(context.initiative_id, amount_cents)
    step_given_amount_cents(context=context, amount_cents=amount_cents)


@given('the merchant generated a transaction of amount {amount_cents} cents')
def step_when_merchant_generated_a_transaction(context, amount_cents):
    step_when_merchant_tries_to_create_a_transaction(context=context, amount_cents=amount_cents)
    step_check_transaction_status(context=context, status='CREATED')
    step_given_amount_cents(context=context, amount_cents=amount_cents)


@then('the transaction is {status}')
def step_check_transaction_status(context, status):
    status = status.upper()
    if status == 'CREATED':
        assert context.create_transaction_response.status_code == 201

        context.latest_trx_details = context.create_transaction_response
        assert 'trxCode' in context.latest_trx_details.json()
        context.trx_code = context.latest_trx_details.json()['trxCode']

        assert 'id' in context.latest_trx_details.json()
        context.trx_id = context.latest_trx_details.json()['id']

        context.latest_trx_details = get_transaction_detail(context.trx_id)
        assert context.latest_trx_details.json()['status'] == status

    if status == 'AUTHORIZED':
        context.latest_trx_details = get_transaction_detail(context.trx_id)
        assert context.latest_trx_details.json()['status'] == status

        step_set_expected_accrued(context)
        assert context.latest_trx_details.json()['rewardCents'] == context.expected_accrued_cents

    if status == 'NOT CREATED':
        assert context.create_transaction_response.status_code != 201

    if status == 'NOT AUTHORIZED':
        assert context.pre_authorization_response.status_code == 403

        context.latest_trx_details = get_transaction_detail(context.trx_id)
        assert context.latest_trx_details.json()['status'] == 'REJECTED'


@given('the merchant generated {trx_num} transactions of amount {amount_cents} cents')
def step_when_merchant_creates_n_transaction_successfully(context, trx_num, amount_cents):
    context.trx_ids = []
    context.trx_codes = []
    step_given_amount_cents(context=context, amount_cents=amount_cents)

    for i in range(int(trx_num)):
        res = post_merchant_create_transaction_acquirer(context.initiative_id, amount_cents)
        context.create_transaction_response = res
        context.latest_trx_details = res
        step_check_transaction_status(context=context, status='CREATED')
        context.trx_ids.append(res.json()['id'])
        context.trx_codes.append(res.json()['trxCode'])


@when('the citizen confirms all the transaction')
def step_when_citizen_authorizes_all_transactions(context):
    for curr_trx_code in context.trx_codes:
        res = put_pre_authorize_payment(curr_trx_code, context.token_io)
        assert res.status_code == 200
        res = put_authorize_payment(curr_trx_code, context.token_io)
        assert res.status_code == 200
        context.latest_trx_details = res
        time.sleep(1)


@given('the citizen\'s budget is eroded')
def step_erode_budget(context):
    trx_amount_to_erode_budget = floor(
        context.budget_per_citizen * 100 * context.budget_per_citizen * context.cashback_percentage)
    step_when_merchant_generated_a_transaction(context=context, amount_cents=trx_amount_to_erode_budget)
    step_when_citizen_authorize_transaction(context=context)


@when('the citizen authorizes the transaction')
def step_when_citizen_authorize_transaction(context):
    res = put_pre_authorize_payment(context.trx_code, context.token_io)
    assert res.status_code == 200

    res = put_authorize_payment(context.trx_code, context.token_io)
    assert res.status_code == 200

    context.latest_trx_details = res


@given('the amount in cents is {amount_cents}')
def step_given_amount_cents(context, amount_cents):
    context.amount_cents = int(amount_cents)
