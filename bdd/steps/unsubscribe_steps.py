from behave import given
from behave import then
from behave import when

from api.idpay import unsubscribe
from util.utility import citizen_unsubscribe_from_initiative
from util.utility import get_io_token


@when('the citizen {citizen_name} tries to unsubscribe')
def step_citizen_tries_to_unsubscribe(context, citizen_name):
    token = get_io_token(context.citizens_fc[citizen_name])
    res = unsubscribe(context.initiative_id, token)
    context.latest_unsubscribe_response = res


@when('the onboard citizen tries to unsubscribe')
def step_citizen_tries_to_unsubscribe(context):
    token = get_io_token(context.eligible_citizen)
    res = unsubscribe(context.initiative_id, token)
    context.latest_unsubscribe_response = res


@then('the latest unsubscribe is {status}')
def step_check_latest_cancellation_failed(context, status):
    status = status.upper()
    if status == 'OK':
        assert context.latest_unsubscribe_response.status_code == 204
    elif (status == 'KO because the initiative has not started yet'.upper() or
          status == 'KO because the citizen is not onboarded'.upper()):
        assert context.latest_unsubscribe_response.status_code == 404
        assert context.latest_unsubscribe_response.json()['code'] == 'WALLET_USER_NOT_ONBOARDED'
    else:
        assert False, f'Uncovered case {status}'


@given('the citizen {citizen_name} is unsubscribed')
@when('the citizen {citizen_name} unsubscribes')
def step_citizen_unsubscribes(context, citizen_name):
    citizen_unsubscribe_from_initiative(initiative_id=context.initiative_id,
                                        fiscal_code=context.citizens_fc[citizen_name])
