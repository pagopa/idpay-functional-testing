import time
from math import floor

from behave import given
from behave import then
from behave import when

from api.idpay import delete_payment_citizen
from api.idpay import delete_payment_merchant
from api.idpay import get_transaction_detail
from api.idpay import post_merchant_create_transaction_acquirer
from api.idpay import put_authorize_payment
from api.idpay import put_pre_authorize_payment
from api.idpay import timeline
from api.mil import delete_transaction_mil
from api.mil import get_transaction_detail_mil
from api.mil import post_merchant_create_transaction_acquirer_mil
from conf.configuration import settings
from util.utility import check_unprocessed_transactions
from util.utility import get_io_token
from util.utility import retry_timeline

default_merchant_name = '1'
timeline_operations = settings.IDPAY.endpoints.timeline.operations


@when('the merchant {merchant_name} tries to generate the transaction {trx_name} of amount {amount_cents} cents')
def step_when_merchant_tries_to_create_a_transaction(context, merchant_name, trx_name, amount_cents):
    curr_merchant_id = context.merchants[merchant_name]['id']
    context.latest_merchant_id = curr_merchant_id

    step_given_amount_cents(context=context, amount_cents=amount_cents)
    context.latest_create_transaction_response = post_merchant_create_transaction_acquirer(
        initiative_id=context.initiative_id,
        amount_cents=amount_cents,
        merchant_id=curr_merchant_id
    )

    context.transactions[trx_name] = context.latest_create_transaction_response


@when(
    'the merchant {merchant_name} tries to generate the transaction {trx_name} of amount {amount_cents} cents through MIL')
def step_when_merchant_tries_to_create_a_transaction_mil(context, merchant_name, trx_name, amount_cents):
    curr_merchant_id = context.merchants[merchant_name]['id']
    curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']
    context.latest_merchant_id = curr_merchant_id

    step_given_amount_cents(context=context, amount_cents=amount_cents)
    context.latest_create_transaction_response = post_merchant_create_transaction_acquirer_mil(
        initiative_id=context.initiative_id,
        amount_cents=amount_cents,
        merchant_fiscal_code=curr_merchant_fiscal_code
    )

    context.transactions[trx_name] = context.latest_create_transaction_response


@when(
    'the merchant {merchant_name} tries to generate the transaction {trx_name} of amount {amount_cents} cents with wrong acquirer ID')
def step_when_merchant_tries_to_create_a_transaction_with_wrong_acquirer_id(context, merchant_name, trx_name,
                                                                            amount_cents):
    curr_merchant_id = context.merchants[merchant_name]['id']
    context.latest_merchant_id = curr_merchant_id

    step_given_amount_cents(context=context, amount_cents=amount_cents)
    context.latest_create_transaction_response = post_merchant_create_transaction_acquirer(
        initiative_id=context.initiative_id,
        amount_cents=amount_cents,
        merchant_id=curr_merchant_id,
        acquirer_id='WRONG_ACQUIRER_ID'
    )

    context.transactions[trx_name] = context.latest_create_transaction_response


@given('the merchant {merchant_name} generates the transaction {trx_name} of amount {amount_cents} cents')
@when('the merchant {merchant_name} generates the transaction {trx_name} of amount {amount_cents} cents')
def step_when_merchant_generated_a_named_transaction(context, merchant_name, trx_name, amount_cents):
    curr_merchant_id = context.merchants[merchant_name]['id']

    step_when_merchant_tries_to_create_a_transaction(context=context, trx_name=trx_name, amount_cents=amount_cents,
                                                     merchant_name=merchant_name)
    assert context.latest_create_transaction_response.status_code == 201

    step_given_amount_cents(context=context, amount_cents=amount_cents)

    context.transactions[trx_name] = get_transaction_detail(context.latest_create_transaction_response.json()['id'],
                                                            merchant_id=curr_merchant_id).json()
    step_check_named_transaction_status(context=context, trx_name=trx_name, expected_status='CREATED')
    context.associated_merchant[trx_name] = merchant_name

    check_unprocessed_transactions(initiative_id=context.initiative_id,
                                   expected_trx_id=context.transactions[trx_name]['id'],
                                   expected_effective_amount=context.transactions[trx_name]['amountCents'],
                                   expected_reward_amount=0,
                                   merchant_id=curr_merchant_id,
                                   expected_status='CREATED'
                                   )


@given('the merchant {merchant_name} generates the transaction {trx_name} of amount {amount_cents} cents through MIL')
@when('the merchant {merchant_name} generates the transaction {trx_name} of amount {amount_cents} cents through MIL')
def step_when_merchant_generated_a_named_transaction_mil(context, merchant_name, trx_name, amount_cents):
    curr_merchant_id = context.merchants[merchant_name]['id']
    curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']

    step_when_merchant_tries_to_create_a_transaction_mil(context=context, trx_name=trx_name, amount_cents=amount_cents,
                                                         merchant_name=merchant_name)
    assert context.latest_create_transaction_response.status_code == 201

    step_given_amount_cents(context=context, amount_cents=amount_cents)
    context.transactions[trx_name] = get_transaction_detail_mil(
        transaction_id=context.latest_create_transaction_response.json()['id'],
        merchant_fiscal_code=curr_merchant_fiscal_code
    ).json()
    step_check_named_transaction_status(context=context, trx_name=trx_name, expected_status='CREATED')
    context.associated_merchant[trx_name] = merchant_name

    check_unprocessed_transactions(initiative_id=context.initiative_id,
                                   expected_trx_id=context.transactions[trx_name]['id'],
                                   expected_effective_amount=context.transactions[trx_name]['amountCents'],
                                   expected_reward_amount=0,
                                   merchant_id=curr_merchant_id,
                                   expected_status='CREATED'
                                   )


@given('the transaction {trx_name} is {expected_status}')
@then('the transaction {trx_name} is {expected_status}')
def step_check_named_transaction_status(context, trx_name, expected_status):
    status = expected_status.upper()
    if status == 'NOT CREATED':
        assert context.latest_create_transaction_response.status_code != 201
        return

    if status == 'NOT CREATED BECAUSE THE MERCHANT IS NOT QUALIFIED':
        assert context.latest_create_transaction_response.status_code == 403
        return

    if status == 'NOT CREATED FOR INVALID AMOUNT':
        assert context.latest_create_transaction_response.status_code == 400
        assert context.latest_create_transaction_response.json()['code'] == 'INVALID AMOUNT'
        assert context.latest_create_transaction_response.json()[
            'message'].startswith('Cannot create transaction with invalid amount: ')
        return

    if status == 'ALREADY AUTHORIZED':
        assert context.latest_pre_authorization_response.status_code == 403
        assert context.latest_pre_authorization_response.json()['code'] == 'PAYMENT_ALREADY_AUTHORIZED'
        assert context.latest_pre_authorization_response.json()[
                   'message'] == f'Transaction with trxCode [{context.transactions[trx_name]["trxCode"]}] is already authorized'
        return

    elif status == 'CANCELLED':
        assert context.latest_cancellation_response.status_code == 200
        res = get_transaction_detail(
            context.transactions[trx_name]['id'],
            merchant_id=context.transactions[trx_name]['merchantId']
        )
        assert res.status_code == 404
        return

    else:
        trx_details = get_transaction_detail(
            context.transactions[trx_name]['id'],
            merchant_id=context.transactions[trx_name]['merchantId']
        ).json()

        if status == 'CREATED':
            assert trx_details['status'] == status
            return

        if status == 'IDENTIFIED':
            assert trx_details['status'] == status
            return

        if status == 'AUTHORIZED':
            assert trx_details['status'] == status
            return

        if status == 'NOT AUTHORIZED':
            assert context.latest_pre_authorization_response.status_code == 403

            assert trx_details['status'] == 'REJECTED'
            assert context.latest_pre_authorization_response.json()['code'] == f'PAYMENT_GENERIC_REJECTED'
            assert context.latest_pre_authorization_response.json()[
                       'message'] == f'Transaction with trxCode [{context.transactions[trx_name]["trxCode"]}] is rejected'
            return

        if status == 'NOT AUTHORIZED FOR BUDGET ERODED':
            assert context.latest_pre_authorization_response.status_code == 403

            assert trx_details['status'] == 'REJECTED'

            assert context.latest_pre_authorization_response.json()['code'] == f'PAYMENT_BUDGET_EXHAUSTED'
            assert context.latest_pre_authorization_response.json()['message'].startswith(
                f'Budget exhausted for user [')
            assert context.latest_pre_authorization_response.json()['message'].endswith(
                f'] and initiative [{context.initiative_id}]')
            return

        if status == 'ALREADY ASSIGNED':
            assert context.latest_pre_authorization_response.status_code == 403

            assert context.latest_pre_authorization_response.json()['code'] == 'PAYMENT_USER_NOT_VALID'
            assert context.latest_pre_authorization_response.json()[
                       'message'] == f'Transaction with trxCode [{context.transactions[trx_name]["trxCode"]}] is already assigned to another user'
            return

        if status == 'EXCEEDING RATE LIMIT':
            assert context.latest_authorization_response.status_code == 429
            assert context.latest_authorization_response.json()['code'] == 'PAYMENT_TOO_MANY_REQUESTS'
            assert context.latest_authorization_response.json()[
                       'message'] == f'Too many request on the ms reward'
            return

    assert False, 'Status not implemented'


@then('every transaction is {expected_status}')
def step_check_every_transaction_status(context, expected_status):
    for i in range(len(context.trx_codes)):
        step_check_named_transaction_status(context=context, trx_name=str(i), expected_status=expected_status)


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


@given('the merchant {merchant_name} generated {trx_num} transactions of amount {amount_cents} cents each through MIL')
def step_when_merchant_creates_n_transaction_successfully_mil(context, merchant_name, trx_num, amount_cents):
    context.trx_ids = []
    context.trx_codes = []
    step_given_amount_cents(context=context, amount_cents=amount_cents)

    for i in range(int(trx_num)):
        step_when_merchant_generated_a_named_transaction_mil(context=context,
                                                             merchant_name=merchant_name,
                                                             trx_name=str(i),
                                                             amount_cents=amount_cents)
        res = context.latest_create_transaction_response
        step_check_named_transaction_status(context=context, trx_name=str(i), expected_status='CREATED')
        context.trx_ids.append(res.json()['id'])
        context.trx_codes.append(res.json()['trxCode'])


@given('the citizen {citizen_name} confirms each transaction')
@when('the citizen {citizen_name} confirms all the transactions')
def step_when_citizen_authorizes_all_transactions(context, citizen_name):
    for i in range(len(context.trx_codes)):
        trx_name = str(i)
        step_when_citizen_confirms_transaction(context=context, citizen_name=citizen_name, trx_name=trx_name)
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
    res = put_pre_authorize_payment(trx_code=trx_code, token=token_io)
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
    associated_merchant_id = context.merchants[context.associated_merchant[trx_name]]['id']

    res = complete_transaction_confirmation(context=context, trx_code=curr_trx_code, token_io=curr_token_io)

    context.authorize_payment_response = res

    step_check_named_transaction_status(context=context, trx_name=trx_name, expected_status='AUTHORIZED')

    update_user_counters(context=context, citizen_name=citizen_name, reward=res.json()['reward'])

    retry_timeline(expected=timeline_operations.transaction, request=timeline,
                   num_required=context.trxs_per_citizen[citizen_name], token=curr_token_io,
                   initiative_id=context.initiative_id, field='operationType', tries=10, delay=3,
                   message='Transaction not received')

    check_unprocessed_transactions(initiative_id=context.initiative_id,
                                   expected_trx_id=context.transactions[trx_name]['id'],
                                   expected_effective_amount=context.transactions[trx_name]['amountCents'],
                                   expected_reward_amount=context.latest_trx_details.json()['reward'],
                                   expected_fiscal_code=context.citizens_fc[citizen_name],
                                   merchant_id=associated_merchant_id,
                                   expected_status='AUTHORIZED'
                                   )

    context.associated_citizen[trx_name] = context.citizens_fc[citizen_name]


@given('the citizen {citizen_name} confirms, immediately before the next step, the transaction {trx_name}')
def step_when_citizen_rapidly_confirms_the_transactions(context, citizen_name, trx_name):
    curr_token_io = get_io_token(context.citizens_fc[citizen_name])

    trx_name = context.transactions[trx_name]['trxCode']

    res = complete_transaction_confirmation(context=context, trx_code=trx_name, token_io=curr_token_io)
    update_user_counters(context=context, citizen_name=citizen_name, reward=res.json()['reward'])
    context.associated_citizen[trx_name] = context.citizens_fc[citizen_name]


@given('the citizen {citizen_name} tries to confirm the transaction {trx_name}')
@when('the citizen {citizen_name} tries to confirm the transaction {trx_name}')
def step_citizen_tries_pre_authorize_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']

    context.latest_pre_authorization_response = put_pre_authorize_payment(trx_code, token_io)

    context.latest_authorization_response = put_authorize_payment(trx_code, token_io)


@given('the citizen {citizen_name} tries to pre-authorize the transaction {trx_name}')
@when('the citizen {citizen_name} tries to pre-authorize the transaction {trx_name}')
def step_citizen_only_pre_authorize_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']

    res = put_pre_authorize_payment(trx_code, token_io)

    context.latest_pre_authorization_response = res


@when('the citizen {citizen_name} pre-authorizes the transaction {trx_name}')
@given('the citizen {citizen_name} pre-authorizes the transaction {trx_name}')
def step_citizen_only_pre_authorize_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']

    res = put_pre_authorize_payment(trx_code, token_io)
    assert res.status_code == 200

    context.latest_pre_authorization_response = res


@given('the citizen {citizen_name} authorizes the transaction {trx_name}')
@when('the citizen {citizen_name} tries to authorize the transaction {trx_name}')
def step_citizen_only_pre_authorize_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']

    context.latest_authorization_response = put_authorize_payment(trx_code, token_io)


@given('the latest pre-authorization fails')
@then('the latest pre-authorization fails')
def step_check_latest_pre_authorization_failed(context):
    assert context.latest_pre_authorization_response.status_code == 403


@then('the latest pre-authorization fails because the transaction no longer exists')
def step_check_latest_pre_authorization_failed_not_found(context):
    assert context.latest_pre_authorization_response.status_code == 404


@then('the latest authorization fails because the transaction no longer exists')
def step_check_latest_authorization_failed(context):
    assert context.latest_authorization_response.status_code == 404


@then('the latest cancellation fails exceeding rate limit')
def step_check_latest_cancellation_failed(context):
    assert context.latest_cancellation_response.status_code == 429


@then('the latest cancellation by citizen fails because the transaction no longer exists')
def step_check_latest_cancellation_by_citizen_failed(context):
    assert context.latest_citizen_cancellation_response.status_code == 404


@given('the amount in cents is {amount_cents}')
def step_given_amount_cents(context, amount_cents):
    context.amount_cents = int(amount_cents)


@given('the merchant {merchant_name} cancels the transaction {trx_name} through MIL')
@when('the merchant {merchant_name} cancels the transaction {trx_name} through MIL')
def step_merchant_cancels_a_transaction_mil(context, merchant_name, trx_name):
    curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']
    curr_trx_id = context.transactions[trx_name]['id']

    res = delete_transaction_mil(transaction_id=curr_trx_id,
                                 merchant_fiscal_code=curr_merchant_fiscal_code
                                 )
    assert res.status_code == 200
    context.latest_cancellation_response = res


@given('the merchant {merchant_name} cancels the transaction {trx_name}')
@when('the merchant {merchant_name} cancels the transaction {trx_name}')
def step_merchant_cancels_a_transaction(context, merchant_name, trx_name):
    curr_merchant_id = context.merchants[merchant_name]['id']
    curr_trx_id = context.transactions[trx_name]['id']

    res = delete_payment_merchant(transaction_id=curr_trx_id,
                                  merchant_id=curr_merchant_id
                                  )
    assert res.status_code == 200
    context.latest_cancellation_response = res


@when('the merchant {merchant_name} tries to cancel the transaction {trx_name} through MIL')
def step_merchant_tries_to_cancels_a_transaction_mil(context, merchant_name, trx_name):
    curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']
    curr_trx_id = context.transactions[trx_name]['id']

    res = delete_transaction_mil(transaction_id=curr_trx_id,
                                 merchant_fiscal_code=curr_merchant_fiscal_code
                                 )
    context.latest_cancellation_response = res


@when('the merchant {merchant_name} tries to cancel the transaction {trx_name}')
def step_merchant_tries_to_cancels_a_transaction(context, merchant_name, trx_name):
    curr_merchant_id = context.merchants[merchant_name]['id']
    curr_trx_id = context.transactions[trx_name]['id']

    res = delete_payment_merchant(transaction_id=curr_trx_id,
                                  merchant_id=curr_merchant_id
                                  )
    context.latest_cancellation_response = res


@given('the merchant {merchant_name} fails cancelling the transaction {trx_name} through MIL')
def step_merchant_tries_to_cancels_a_transaction_and_fails_mil(context, merchant_name, trx_name):
    curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']
    curr_trx_id = context.transactions[trx_name]['id']

    res = delete_transaction_mil(transaction_id=curr_trx_id,
                                 merchant_fiscal_code=curr_merchant_fiscal_code
                                 )
    assert res.status_code == 429
    context.latest_cancellation_response = res


@given('the merchant {merchant_name} fails cancelling the transaction {trx_name}')
def step_merchant_tries_to_cancels_a_transaction_and_fails(context, merchant_name, trx_name):
    curr_merchant_id = context.merchants[merchant_name]['id']
    curr_trx_id = context.transactions[trx_name]['id']

    res = delete_payment_merchant(transaction_id=curr_trx_id,
                                  merchant_id=curr_merchant_id
                                  )
    assert res.status_code == 429
    context.latest_cancellation_response = res


@when('the merchant {merchant_name} cancels every transaction through MIL')
def step_merchant_cancels_every_transaction_mil(context, merchant_name):
    for curr_trx_id in context.trx_ids:
        curr_merchant_fiscal_code = context.merchants[merchant_name]['fiscal_code']
        curr_trx_id = curr_trx_id

        res = delete_transaction_mil(transaction_id=curr_trx_id,
                                     merchant_fiscal_code=curr_merchant_fiscal_code
                                     )

        assert res.status_code == 200

        context.latest_cancellation_response = res

        time.sleep(1)


@when('the merchant {merchant_name} cancels every transaction')
def step_merchant_cancels_every_transaction(context, merchant_name):
    for curr_trx_id in context.trx_ids:
        curr_merchant_id = context.merchants[merchant_name]['id']
        curr_trx_id = curr_trx_id

        res = delete_payment_merchant(transaction_id=curr_trx_id,
                                      merchant_id=curr_merchant_id
                                      )

        assert res.status_code == 200

        context.latest_cancellation_response = res

        time.sleep(1)


@given('the citizen {citizen_name} cancels the transaction {trx_name}')
@when('the citizen {citizen_name} cancels the transaction {trx_name}')
def step_citizen_cancels_a_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']

    res = delete_payment_citizen(trx_code=trx_code,
                                 token=token_io)
    assert res.status_code == 200
    context.latest_citizen_cancellation_response = res


@when('the citizen {citizen_name} tries to cancel the transaction {trx_name}')
def step_citizen_tries_to_cancel_a_transaction(context, citizen_name, trx_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    trx_code = context.transactions[trx_name]['trxCode']

    res = delete_payment_citizen(trx_code=trx_code,
                                 token=token_io)
    context.latest_citizen_cancellation_response = res


def update_user_counters(context, citizen_name, reward):
    if citizen_name not in context.accrued_per_citizen.keys():
        context.accrued_per_citizen[citizen_name] = reward
        context.trxs_per_citizen[citizen_name] = 1
    else:
        context.accrued_per_citizen[citizen_name] = context.accrued_per_citizen[citizen_name] + reward
        context.trxs_per_citizen[citizen_name] = context.trxs_per_citizen[citizen_name] + 1

    context.total_accrued = context.total_accrued + reward
    context.num_new_trxs = context.num_new_trxs + 1
