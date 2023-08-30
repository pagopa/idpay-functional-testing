from behave import given
from behave import then
from behave import when

from api.idpay import put_user_id_suspension
from bdd.steps.onboarding_steps import step_check_onboarding_status
from util.utility import suspend_citizen_from_initiative
from util.utility import tokenize_fc


@when('the institution suspends the citizen {citizen_name}')
def step_institution_suspends_citizen(context, citizen_name):
    suspend_citizen_from_initiative(initiative_id=context.initiative_id, fiscal_code=context.citizens_fc[citizen_name])


@when('the institution tries to suspend the citizen {citizen_name}')
def step_institution_tries_citizen_suspension(context, citizen_name):
    token = tokenize_fc(fiscal_code=context.citizens_fc[citizen_name])
    res = put_user_id_suspension(initiative_id=context.initiative_id, user_id=token)
    context.latest_suspension_response = res


@given('the institution suspends correctly the citizen {citizen_name}')
@when('the institution suspends correctly the citizen {citizen_name}')
def step_institution_suspends_correctly_citizen(context, citizen_name):
    step_institution_suspends_citizen(context=context, citizen_name=citizen_name)
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='SUSPENDED')


@then('the latest suspension fails not finding the citizen')
def step_check_latest_suspension(context):
    assert context.latest_suspension_response.status_code == 404
    assert context.latest_suspension_response.json()['code'] == 404
    assert context.latest_suspension_response.json()[
               'message'] == 'The requested initiative is not active for the current user!'
