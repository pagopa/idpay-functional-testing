from behave import given
from behave import then
from behave import when

from api.idpay import post_create_payment_bar_code
from api.idpay import put_authorize_bar_code_merchant
from util.utility import get_io_token


@given('the citizen {citizen_name} creates the transaction {trx_name} by Bar Code')
def step_citizen_create_bar_code(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    response = post_create_payment_bar_code(token=token_io,
                                            initiative_id=context.initiative_id)

    assert response.status_code == 201
    assert response.json()['status'] == 'CREATED'

    context.transactions[trx_name] = response.json()


@when('the citizen {citizen_name} tries to create the transaction {trx_name} by Bar Code')
def step_citizen_create_bar_code(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    response = post_create_payment_bar_code(token=token_io,
                                            initiative_id=context.initiative_id)

    context.latest_citizen_creation_bar_code = response


@then('the latest transaction creation by citizen fails because {reason_ko}')
def step_check_latest_citizen_creation_bar_code(context, reason_ko):
    reason_ko = reason_ko.upper()

    if reason_ko == 'THE BUDGET IS EXHAUSTED':
        assert context.latest_citizen_creation_bar_code.status_code == 403
        assert context.latest_citizen_creation_bar_code.json()['code'] == 'PAYMENT_BUDGET_EXHAUSTED'
        assert context.latest_citizen_creation_bar_code.json()[
                   'message'] == f'The budget related to the user on initiativeId [{context.initiative_id}] was exhausted.'

    if reason_ko == 'THE CITIZEN IS NOT ONBOARDED':
        assert context.latest_citizen_creation_bar_code.status_code == 403
        assert context.latest_citizen_creation_bar_code.json()['code'] == 'PAYMENT_USER_NOT_ONBOARDED'
        assert context.latest_citizen_creation_bar_code.json()[
                   'message'] == f'The user is not onboarded on initiative [{context.initiative_id}].'


@when('the merchant {merchant_name} authorizes the transaction {trx_name} by Bar Code of amount {amount_cents} cents')
@given('the merchant {merchant_name} authorizes the transaction {trx_name} by Bar Code of amount {amount_cents} cents')
def step_merchant_authorize_bar_code(context, merchant_name, trx_name, amount_cents):
    step_merchant_try_to_authorize_bar_code(context=context, merchant_name=merchant_name,
                                            trx_name=trx_name, amount_cents=amount_cents)

    assert context.latest_merchant_authorization_bar_code.status_code == 200
    context.transactions[trx_name] = context.latest_merchant_authorization_bar_code.json()
    context.associated_merchant[trx_name] = merchant_name


@when('the merchant {merchant_name} tries to authorize the transaction {trx_name} by Bar Code of amount {amount_cents} cents')
def step_merchant_try_to_authorize_bar_code(context, merchant_name, trx_name, amount_cents):
    curr_merchant_id = context.merchants[merchant_name]['id']
    trx_code = context.transactions[trx_name]['trxCode']

    context.latest_merchant_authorization_bar_code = put_authorize_bar_code_merchant(merchant_id=curr_merchant_id,
                                                                                     trx_code=trx_code,
                                                                                     amount_cents=amount_cents)


@then('with Bar Code the transaction {trx_name} is {expected_status}')
@given('with Bar Code the transaction {trx_name} is {expected_status}')
def step_check_detail_transaction_bar_code(context, trx_name, expected_status):
    status = expected_status.upper()

    if status == 'AUTHORIZED':
        assert context.transactions[trx_name]['status'] == 'AUTHORIZED'


@then('the latest authorization by merchant fails because {reason_ko}')
def step_check_latest_merchant_authorized_bar_code(context, reason_ko):
    reason_ko = reason_ko.upper()

    if reason_ko == 'THE TRANSACTION IS NOT FOUND':
        assert context.latest_merchant_authorization_bar_code.status_code == 404
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_NOT_FOUND_EXPIRED'
        assert context.latest_merchant_authorization_bar_code.json()[
                   'message'].startswith('Cannot find transaction with trxCode')

    if reason_ko == 'THE TRANSACTION IS ALREADY AUTHORIZED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_ALREADY_AUTHORIZED'
        assert context.latest_merchant_authorization_bar_code.json()['message'].startswith('Transaction with trxCode')
        assert context.latest_merchant_authorization_bar_code.json()['message'].endswith('is already authorized')

    if reason_ko == 'THE CITIZEN IS SUSPENDED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_USER_SUSPENDED'
        assert context.latest_merchant_authorization_bar_code.json()[
                   'message'] == f'The user has been suspended for initiative [{context.initiative_id}]'

    if reason_ko == 'THE CITIZEN IS UNSUBSCRIBED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_USER_UNSUBSCRIBED'
        assert context.latest_merchant_authorization_bar_code.json()[
                   'message'] == f'The user has unsubscribed from initiative [{context.initiative_id}]'

    if reason_ko == 'THE BUDGET IS EXHAUSTED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_BUDGET_EXHAUSTED'
        #TODO fix message
        #assert context.latest_merchant_authorization_bar_code.json()[
        #           'message'] == f'The budget related to the user on initiativeId [{context.initiative_id}] was exhausted.'