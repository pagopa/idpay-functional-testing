from behave import given
from behave import then
from behave import when

from api.idpay import post_create_payment_bar_code, put_authorize_bar_code_merchant
from util.utility import get_io_token, tokenize_fc


@given('the citizen {citizen_name} creates the transaction {trx_name} by Bar Code')
def step_citizen_create_bar_code(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    response = post_create_payment_bar_code(token=token_io,
                                            initiative_id=context.initiative_id)

    assert response.status_code == 201
    assert response.json()['status'] == 'CREATED'

    context.transactions[trx_name] = response.json()


@when('the merchant {merchant_name} authorizes the transaction {trx_name} by Bar Code of amount {amount_cents} cents')
def step_merchant_authorize_bar_code(context, merchant_name, trx_name, amount_cents):
    step_merchant_try_to_authorize_bar_code(context=context, merchant_name=merchant_name,
                                            trx_name=trx_name, amount_cents=amount_cents)

    assert context.latest_merchant_authorization_bar_code.status_code == 200
    context.transactions[trx_name] = context.latest_merchant_authorization_bar_code.json()
    context.amount_cents[trx_name] = amount_cents


@when('the merchant {merchant_name} tries to authorize the transaction {trx_name} by Bar Code of amount {amount_cents} cents')
def step_merchant_try_to_authorize_bar_code(context, merchant_name, trx_name, amount_cents):
    curr_merchant_id = context.merchants[merchant_name]['id']
    trx_code = context.transactions[trx_name]['trxCode']

    context.latest_merchant_authorization_bar_code = put_authorize_bar_code_merchant(merchant_id=curr_merchant_id,
                                                                                     trx_code=trx_code,
                                                                                     amount_cents=amount_cents)


@then('the payment of transaction {trx_name} is {expected_status}')
def step_check_detail_transaction_bar_code(context, trx_name, expected_status):
    status = expected_status.upper()

    if status == 'AUTHORIZED':
        assert context.transactions[trx_name]['status'] == 'AUTHORIZED'
        assert context.transactions[trx_name]['amountCents'] == context.amount_cents[trx_name]


@then('the latest authorization by merchant fails because the transaction {trx_name} is {reason_ko}')
def step_check_latest_merchant_authorized_bar_code_trx(context, trx_name, reason_ko):
    reason_ko = reason_ko.upper()
    trx_code = context.transactions[trx_name]['trxCode']

    if reason_ko == 'NOT FOUND':
        assert context.latest_merchant_authorization_bar_code.status_code == 404
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_NOT_FOUND_EXPIRED'
        assert context.latest_merchant_authorization_bar_code.json()[
                   'message'] == f'Cannot find transaction with trxCode [{trx_code}]'

    if reason_ko == 'ALREADY AUTHORIZED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_ALREADY_AUTHORIZED'
        assert context.latest_merchant_authorization_bar_code.json()[
                   'message'] == f'Transaction with trxCode [{trx_code}] is already authorized'


@then('the latest authorization by merchant fails because the citizen {citizen_name} is {reason_ko}')
def step_check_latest_merchant_authorized_bar_code_citizen(context, citizen_name, reason_ko):
    reason_ko = reason_ko.upper()
    curr_tokenized_fc = tokenize_fc(context.citizens_fc[citizen_name])

    if reason_ko == 'SUSPENDED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_USER_SUSPENDED'
        assert context.latest_merchant_authorization_bar_code.json()[
                   'message'] == f'User {curr_tokenized_fc} has been suspended for initiative {context.initiative_id}'

    if reason_ko == 'UNSUBSCRIBED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_USER_UNSUBSCRIBED'
        assert context.latest_merchant_authorization_bar_code.json()[
                   'message'] == f'User {curr_tokenized_fc} is unsubscribed from initiative {context.initiative_id}'
