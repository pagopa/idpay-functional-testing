from behave import given
from behave import then
from behave import when

from api.idpay import put_citizen_readmission
from api.idpay import put_citizen_suspension
from bdd.steps.onboarding_steps import step_check_onboarding_status
from conf.configuration import secrets
from util.utility import get_selfcare_token
from util.utility import readmit_citizen_to_initiative
from util.utility import suspend_citizen_from_initiative


@given('the institution suspends the citizen {citizen_name}')
@when('the institution suspends the citizen {citizen_name}')
def step_institution_suspends_citizen(context, citizen_name):
    suspend_citizen_from_initiative(initiative_id=context.initiative_id, fiscal_code=context.citizens_fc[citizen_name])


@when('the institution tries to suspend the citizen {citizen_name}')
def step_institution_tries_citizen_suspension(context, citizen_name):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = put_citizen_suspension(selfcare_token=institution_token, initiative_id=context.initiative_id,
                                 fiscal_code=context.citizens_fc[citizen_name])
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


@when('the institution tries to readmit the citizen {citizen_name}')
def step_institution_tries_citizen_readmission(context, citizen_name):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = put_citizen_readmission(selfcare_token=institution_token, initiative_id=context.initiative_id,
                                  fiscal_code=context.citizens_fc[citizen_name])
    context.latest_readmission_response = res


@given('the institution readmits correctly the citizen {citizen_name}')
@when('the institution readmits correctly the citizen {citizen_name}')
def step_institution_suspends_correctly_citizen(context, citizen_name):
    readmit_citizen_to_initiative(initiative_id=context.initiative_id, fiscal_code=context.citizens_fc[citizen_name])
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='READMITTED')


@then('the latest readmission fails not finding the citizen')
def step_check_latest_readmission(context):
    assert context.latest_readmission_response.status_code == 404
    assert context.latest_readmission_response.json()['code'] == 404
    assert context.latest_readmission_response.json()[
               'message'] == 'The requested initiative is not active for the current user!'
