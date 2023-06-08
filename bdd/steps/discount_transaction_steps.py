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
from conf.configuration import secrets
from util.utility import get_io_token

merchant_id = secrets.merchant_id


@when('the merchant tries to generate the transaction {trx_name} of amount {amount_cents} cents')
def step_when_merchant_tries_to_create_a_transaction(context, trx_name, amount_cents):
    step_given_amount_cents(context=context, amount_cents=amount_cents)
    context.transactions[trx_name] = post_merchant_create_transaction_acquirer(
        initiative_id=context.initiative_id,
        amount_cents=amount_cents,
        merchant_id=context.merchant_id,
        trx_date=context.trx_date
    )


@given('the merchant generates the transaction {trx_name} of amount {amount_cents} cents')
def step_when_merchant_generated_a_named_transaction(context, trx_name, amount_cents):
    step_when_merchant_tries_to_create_a_transaction(context=context, trx_name=trx_name, amount_cents=amount_cents)
    assert context.transactions[trx_name].status_code == 201

    step_check_named_transaction_status(context=context, trx_name=trx_name, expected_status='CREATED')
    step_given_amount_cents(context=context, amount_cents=amount_cents)

    context.transactions[trx_name] = get_transaction_detail(context.transactions[trx_name].json()['id'],
                                                            merchant_id=merchant_id).json()


@then('the transaction {trx_name} is {expected_status}')
def step_check_named_transaction_status(context, trx_name, expected_status):
    status = expected_status.upper()
    if status == 'NOT CREATED':
        assert context.transactions[trx_name].status_code != 201
    else:
        print(context.transactions[trx_name])
        trx_details = get_transaction_detail(
            context.transactions[trx_name].json()['id'],
            merchant_id=merchant_id
        ).json()

        if status == 'CREATED':
            assert trx_details['status'] == status

        if status == 'AUTHORIZED':
            assert trx_details['status'] == status

        if status == 'NOT CREATED':
            print(context.latest_create_transaction_response.json())
            assert context.latest_create_transaction_response.status_code != 201

        if status == 'NOT AUTHORIZED':
            assert context.pre_authorization_response.status_code == 403

            assert trx_details['status'] == 'REJECTED'


@given('the merchant generated {trx_num} transactions of amount {amount_cents} cents each')
def step_when_merchant_creates_n_transaction_successfully(context, trx_num, amount_cents):
    context.trx_ids = []
    context.trx_codes = []
    step_given_amount_cents(context=context, amount_cents=amount_cents)

    for i in range(int(trx_num)):
        res = post_merchant_create_transaction_acquirer(initiative_id=context.initiative_id,
                                                        amount_cents=amount_cents,
                                                        merchant_id=merchant_id,
                                                        trx_date=context.trx_date)
        context.transactions[str(i)] = res
        context.create_transaction_response = res
        context.latest_trx_details = res
        step_check_named_transaction_status(context=context, trx_name=str(i), expected_status='CREATED')
        context.trx_ids.append(res.json()['id'])
        context.trx_codes.append(res.json()['trxCode'])


@when('the citizen {citizen_name} confirms all the transaction')
def step_when_citizen_authorizes_all_transactions(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    for curr_trx_code in context.trx_codes:
        res = put_pre_authorize_payment(curr_trx_code, token_io)
        assert res.status_code == 200
        res = put_authorize_payment(curr_trx_code, token_io)
        assert res.status_code == 200
        context.latest_trx_details = res
        time.sleep(1)


@given('the citizen {citizen_name}\'s budget is eroded')
def step_erode_budget(context, citizen_name):
    erode_budget_trx = 'ERODING_BUDGET_TRX'
    trx_amount_to_erode_budget = floor(
        context.budget_per_citizen * 100 * context.budget_per_citizen * context.cashback_percentage)
    step_when_merchant_generated_a_named_transaction(context=context, trx_name=erode_budget_trx,
                                                     amount_cents=trx_amount_to_erode_budget)
    step_when_citizen_confirms_transaction(context=context, citizen_name=citizen_name, trx_name=erode_budget_trx)


@when('the citizen authorizes the transaction')
def step_when_citizen_authorize_transaction(context):
    latest_token_io = get_io_token(context.latest_citizen_fc)
    complete_transaction_confirmation(context=context, token_io=latest_token_io)


@when('the citizen {citizen_name} authorizes the transaction')
def step_when_named_citizen_authorize_transaction(context, citizen_name):
    latest_token_io = get_io_token(context.citizens_fc[citizen_name])
    complete_transaction_confirmation(context=context, token_io=latest_token_io)


def complete_transaction_confirmation(context, token_io):
    res = put_pre_authorize_payment(context.latest_trx_code, token_io)
    assert res.status_code == 200

    res = put_authorize_payment(context.latest_trx_code, token_io)
    assert res.status_code == 200

    context.latest_trx_details = res


@when('the citizen authorizes the transaction {trx_name}')
def step_when_citizen_authorize_transaction(context, trx_name):
    curr_token_io = get_io_token(context.latest_citizen_fc)
    res = put_pre_authorize_payment(context.transactions[trx_name]['trxCode'], curr_token_io)
    print(res)
    assert res.status_code == 200

    res = put_authorize_payment(context.transactions[trx_name]['trxCode'], curr_token_io)
    assert res.status_code == 200

    context.latest_trx_details = res


@when('the citizen {citizen_name} confirms the transaction {trx_name}')
def step_when_citizen_confirms_transaction(context, citizen_name, trx_name):
    curr_token_io = get_io_token(context.citizens_fc[citizen_name])
    res = put_pre_authorize_payment(context.transactions[trx_name]['trxCode'], curr_token_io)
    assert res.status_code == 200

    res = put_authorize_payment(context.transactions[trx_name]['trxCode'], curr_token_io)
    assert res.status_code == 200

    context.authorize_payment_response = res

    step_set_expected_accrued(context)
    print(context.authorize_payment_response.json())
    print(context.expected_accrued_cents)
    assert context.authorize_payment_response.json()['reward'] == context.expected_accrued_cents


@when('the citizen {citizen_name} tries to confirm the transaction {trx_name}')
def step_citizen_tries_pre_authorize_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']
    context.pre_authorization_response = put_pre_authorize_payment(trx_code, token_io)


@given('the amount in cents is {amount_cents}')
def step_given_amount_cents(context, amount_cents):
    context.amount_cents = int(amount_cents)


@then('the transaction {trx_name} expires')
def step_transaction_expires(context, trx_name):
    pass
