from behave import given
from behave import then
from behave import when

from api.idpay import get_payment_instruments
from api.idpay import get_transaction_detail
from api.idpay import post_create_payment_bar_code
from api.idpay import put_authorize_bar_code_merchant
from api.idpay import wallet
from conf.configuration import settings
from util.utility import get_io_token
from util.utility import retry_payment_instrument
from util.utility import retry_wallet

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses
instrument_types = settings.IDPAY.endpoints.wallet.instrument_type


def step_check_citizen_is_enabled_to_app_io_payment_method(context, citizen_name):
    # Every citizen onboarded to discount initiative is enabled to pay by Bar Code or QR Code
    # (considered as 'App IO Payment')
    token = get_io_token(context.citizens_fc[citizen_name])

    citizen_wallet = retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token,
                                  initiative_id=context.initiative_id, field='status', tries=3, delay=3)

    assert citizen_wallet.json()['nInstr'] == 1
    retry_payment_instrument(expected_type=instrument_types.app_io_payment, expected_status='ACTIVE',
                             request=get_payment_instruments, token=token, initiative_id=context.initiative_id,
                             field_type='instrumentType', field_status='status', num_required=1, tries=10, delay=2)


@given('the citizen {citizen_name} creates the transaction {trx_name} by Bar Code')
@when('the citizen {citizen_name} creates the transaction {trx_name} by Bar Code')
def step_citizen_create_bar_code(context, citizen_name, trx_name):
    step_check_citizen_is_enabled_to_app_io_payment_method(context=context, citizen_name=citizen_name)
    token_io = get_io_token(context.citizens_fc[citizen_name])
    response = post_create_payment_bar_code(token=token_io,
                                            initiative_id=context.initiative_id)

    assert response.status_code == 201
    assert response.json()['status'] == 'CREATED'

    context.transactions[trx_name] = response.json()
    context.associated_citizen[trx_name] = context.citizens_fc[citizen_name]


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

    if reason_ko == 'THE CITIZEN IS NOT ONBOARDED':
        assert context.latest_citizen_creation_bar_code.status_code == 403
        assert context.latest_citizen_creation_bar_code.json()['code'] == 'PAYMENT_USER_NOT_ONBOARDED'

    if reason_ko == 'THE CITIZEN IS UNSUBSCRIBED':
        assert context.latest_citizen_creation_bar_code.status_code == 403
        assert context.latest_citizen_creation_bar_code.json()['code'] == 'PAYMENT_USER_UNSUBSCRIBED'

    if reason_ko == 'IS OUT OF VALID PERIOD':
        assert context.latest_citizen_creation_bar_code.status_code == 403
        assert context.latest_citizen_creation_bar_code.json()['code'] == 'PAYMENT_INITIATIVE_INVALID_DATE'


@when('the merchant {merchant_name} authorizes the transaction {trx_name} by Bar Code of amount {amount_cents} cents')
@given('the merchant {merchant_name} authorizes the transaction {trx_name} by Bar Code of amount {amount_cents} cents')
def step_merchant_authorize_bar_code(context, merchant_name, trx_name, amount_cents):
    step_merchant_try_to_authorize_bar_code(context=context, merchant_name=merchant_name,
                                            trx_name=trx_name, amount_cents=amount_cents)

    assert context.latest_merchant_authorization_bar_code.status_code == 200
    context.associated_merchant[trx_name] = merchant_name
    step_check_detail_transaction_bar_code(context=context, trx_name=trx_name, expected_status='AUTHORIZED')


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

    if status == 'CREATED':
        assert context.transactions[trx_name]['status'] == 'CREATED'
        return

    res = get_transaction_detail(
        context.transactions[trx_name]['id'],
        merchant_id=context.merchants[context.associated_merchant[trx_name]]['id']
    )

    if status == 'AUTHORIZED':
        assert res.status_code == 200
        assert res.json()['status'] == 'AUTHORIZED'
        return

    elif status == 'CANCELLED':
        assert context.latest_cancellation_response.status_code == 200
        assert res.status_code == 404
        return


@then('the latest authorization by merchant fails because {reason_ko}')
def step_check_latest_merchant_authorized_bar_code(context, reason_ko):
    reason_ko = reason_ko.upper()

    if reason_ko == 'THE TRANSACTION IS NOT FOUND':
        assert context.latest_merchant_authorization_bar_code.status_code == 404
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_NOT_FOUND_OR_EXPIRED'

    elif reason_ko == 'THE TRANSACTION IS ALREADY AUTHORIZED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_ALREADY_AUTHORIZED'

    elif reason_ko == 'THE CITIZEN IS SUSPENDED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_USER_SUSPENDED'

    elif reason_ko == 'THE CITIZEN IS UNSUBSCRIBED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_USER_UNSUBSCRIBED'

    elif reason_ko == 'THE BUDGET IS EXHAUSTED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_BUDGET_EXHAUSTED'

    elif reason_ko == 'THE MERCHANT IS NOT QUALIFIED':
        assert context.latest_merchant_authorization_bar_code.status_code == 403
        assert context.latest_merchant_authorization_bar_code.json()['code'] == 'PAYMENT_MERCHANT_NOT_ONBOARDED'
