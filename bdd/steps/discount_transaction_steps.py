import time
from math import floor

from behave import given
from behave import then
from behave import when

from api.idpay import get_transaction_detail
from api.idpay import post_merchant_create_transaction_acquirer
from api.idpay import put_authorize_payment
from api.idpay import put_pre_authorize_payment
from util.utility import get_io_token

default_merchant_name = '1'


@when('the merchant {merchant_name} tries to generate the transaction {trx_name} of amount {amount_cents} cents')
def step_when_merchant_tries_to_create_a_transaction(context, merchant_name, trx_name, amount_cents):
    curr_merchant_id = context.merchant_ids[merchant_name]
    context.latest_merchant_id = curr_merchant_id

    step_given_amount_cents(context=context, amount_cents=amount_cents)
    context.latest_create_transaction_response = post_merchant_create_transaction_acquirer(
        initiative_id=context.initiative_id,
        amount_cents=amount_cents,
        merchant_id=curr_merchant_id,
        trx_date=context.trx_date
    )


@given('the merchant {merchant_name} generates the transaction {trx_name} of amount {amount_cents} cents')
@when('the merchant {merchant_name} generates the transaction {trx_name} of amount {amount_cents} cents')
def step_when_merchant_generated_a_named_transaction(context, merchant_name, trx_name, amount_cents):
    step_when_merchant_tries_to_create_a_transaction(context=context, trx_name=trx_name, amount_cents=amount_cents,
                                                     merchant_name=merchant_name)
    assert context.latest_create_transaction_response.status_code == 201

    step_given_amount_cents(context=context, amount_cents=amount_cents)

    context.transactions[trx_name] = get_transaction_detail(context.latest_create_transaction_response.json()['id'],
                                                            merchant_id=context.latest_merchant_id).json()
    step_check_named_transaction_status(context=context, trx_name=trx_name, expected_status='CREATED')


@then('the transaction {trx_name} is {expected_status}')
def step_check_named_transaction_status(context, trx_name, expected_status):
    status = expected_status.upper()
    if status == 'NOT CREATED':
        assert context.latest_create_transaction_response.status_code != 201
    else:
        trx_details = get_transaction_detail(
            context.transactions[trx_name]['id'],
            merchant_id=context.latest_merchant_id
        ).json()

        if status == 'CREATED':
            assert trx_details['status'] == status

        if status == 'IDENTIFIED':
            assert trx_details['status'] == status

        if status == 'AUTHORIZED':
            assert trx_details['status'] == status

        if status == 'NOT CREATED':
            assert context.latest_create_transaction_response.status_code != 201

        if status == 'NOT AUTHORIZED':
            assert context.latest_pre_authorization_response.status_code == 403

            assert trx_details['status'] == 'REJECTED'

        if status == 'ALREADY CONFIRMED':
            assert context.latest_pre_authorization_response.status_code == 403

            assert context.latest_pre_authorization_response.json()['code'] == 'FORBIDDEN'
            assert context.latest_pre_authorization_response.json()[
                       'message'] == f'Transaction with trxCode [{context.transactions[trx_name]["trxCode"]}] is already assigned to another user'

        if status == 'EXCEEDING RATE LIMIT':
            assert context.latest_authorization_response.status_code == 429

            assert context.latest_authorization_response.json()['code'] == 'REWARD CALCULATOR'
            assert context.latest_authorization_response.json()[
                       'message'] == f'Too many request on the ms reward'


@given('the merchant {merchant_name} generated {trx_num} transactions of amount {amount_cents} cents each')
def step_when_merchant_creates_n_transaction_successfully(context, merchant_name, trx_num, amount_cents):
    context.trx_ids = []
    context.trx_codes = []
    step_given_amount_cents(context=context, amount_cents=amount_cents)

    for i in range(int(trx_num)):
        step_when_merchant_generated_a_named_transaction(context=context,
                                                         merchant_name=merchant_name,
                                                         trx_name=str(i),
                                                         amount_cents=amount_cents)
        res = context.latest_create_transaction_response
        step_check_named_transaction_status(context=context, trx_name=str(i), expected_status='CREATED')
        context.trx_ids.append(res.json()['id'])
        context.trx_codes.append(res.json()['trxCode'])


@when('the citizen {citizen_name} confirms all the transaction')
def step_when_citizen_authorizes_all_transactions(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    for curr_trx_code in context.trx_codes:
        res = complete_transaction_confirmation(context=context, trx_code=curr_trx_code, token_io=token_io)

        if citizen_name not in context.accrued_per_citizen.keys():
            context.accrued_per_citizen[citizen_name] = res.json()['reward']
        else:
            context.accrued_per_citizen[citizen_name] = context.accrued_per_citizen[citizen_name] + res.json()['reward']

        time.sleep(1)


@given('the citizen {citizen_name}\'s budget is eroded')
def step_erode_budget(context, citizen_name):
    erode_budget_trx = 'ERODING_BUDGET_TRX'
    trx_amount_to_erode_budget = floor(
        context.budget_per_citizen * 100 * context.budget_per_citizen * context.cashback_percentage)
    step_when_merchant_generated_a_named_transaction(context=context, trx_name=erode_budget_trx,
                                                     amount_cents=trx_amount_to_erode_budget,
                                                     merchant_name=default_merchant_name)
    step_when_citizen_confirms_transaction(context=context, citizen_name=citizen_name, trx_name=erode_budget_trx)


def complete_transaction_confirmation(context, trx_code, token_io):
    res = put_pre_authorize_payment(trx_code, token_io)
    assert res.status_code == 200

    res = put_authorize_payment(trx_code, token_io)
    assert res.status_code == 200

    context.latest_trx_details = res
    return res


@when('the citizen {citizen_name} confirms the transaction {trx_name}')
@given('the citizen {citizen_name} confirms the transaction {trx_name}')
def step_when_citizen_confirms_transaction(context, citizen_name, trx_name):
    curr_trx_code = context.transactions[trx_name]['trxCode']
    curr_token_io = get_io_token(context.citizens_fc[citizen_name])
    res = complete_transaction_confirmation(context=context, trx_code=curr_trx_code, token_io=curr_token_io)

    context.authorize_payment_response = res

    if citizen_name not in context.accrued_per_citizen.keys():
        context.accrued_per_citizen[citizen_name] = res.json()['reward']
    else:
        context.accrued_per_citizen[citizen_name] = context.accrued_per_citizen[citizen_name] + res.json()['reward']


@when('the citizen {citizen_name} tries to confirm the transaction {trx_name}')
def step_citizen_tries_pre_authorize_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']

    context.latest_pre_authorization_response = put_pre_authorize_payment(trx_code, token_io)

    context.latest_authorization_response = put_authorize_payment(trx_code, token_io)


@given('the citizen {citizen_name} pre-authorizes the transaction {trx_name}')
@when('the citizen {citizen_name} tries to pre-authorize the transaction {trx_name}')
def step_citizen_only_pre_authorize_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']

    context.latest_pre_authorization_response = put_pre_authorize_payment(trx_code, token_io)


@then('the latest pre-authorization fails')
def step_check_latest_pre_authorization_failed(context):
    assert context.latest_pre_authorization_response.status_code == 403


@given('the amount in cents is {amount_cents}')
def step_given_amount_cents(context, amount_cents):
    context.amount_cents = int(amount_cents)


@then('the transaction {trx_name} expires')
def step_transaction_expires(context, trx_name):
    pass
