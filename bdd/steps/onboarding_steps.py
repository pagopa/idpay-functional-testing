import requests
from behave import given
from behave import then
from behave import when

from api.idpay import wallet
from api.onboarding_io import accept_terms_and_condition
from api.onboarding_io import status_onboarding
from conf.configuration import secrets
from conf.configuration import settings
from util.dataset_utility import fake_iban
from util.dataset_utility import fake_pan
from util.utility import card_enroll
from util.utility import get_io_token
from util.utility import iban_enroll
from util.utility import retry_io_onboarding
from util.utility import retry_wallet

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses
timeline_operations = settings.IDPAY.endpoints.timeline.operations


@given('the citizen {citizen_name} onboarded')
@given('the citizen {citizen_name} is onboard')
def step_named_citizen_onboard(context, citizen_name):
    step_citizen_accept_terms_and_condition(context=context, citizen_name=citizen_name)
    step_insert_self_declared_criteria(context=context, citizen_name=citizen_name, correctness='correctly')
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='OK')


@given('the citizen {citizen_name} is not onboard')
def step_citizen_not_onboard(context, citizen_name):
    step_citizen_accept_terms_and_condition(context=context, citizen_name=citizen_name)
    step_insert_self_declared_criteria(context=context, citizen_name=citizen_name, correctness='not correctly')


@when('the citizen {citizen_name} tries to onboard')
def step_citizen_tries_to_onboard(context, citizen_name):
    step_citizen_accept_terms_and_condition(context=context, citizen_name=citizen_name)
    step_insert_self_declared_criteria(context=context, citizen_name=citizen_name, correctness='correctly')


@given('the citizen {citizen_name} accepts terms and condition')
def step_citizen_accept_terms_and_condition(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.accept_tc_response = accept_terms_and_condition(token=token_io, initiative_id=context.initiative_id)
    assert context.accept_tc_response.status_code == 204


@then('the onboard of {citizen_name} is {status}')
def step_check_onboarding_status(context, citizen_name, status):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = status_onboarding(token_io, context.initiative_id)
    assert res.status_code == 200

    if status == 'pending':
        expected_status = 'ACCEPTED_TC'
    else:
        expected_status = f'ONBOARDING_{status}'

    retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                        initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
                        message=f'Citizen onboard not {status}')


@when('the citizen {citizen_name} insert self-declared criteria {correctness}')
def step_insert_self_declared_criteria(context, citizen_name, correctness):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    if correctness == 'not correctly':
        pdnd_accept = 'false'
        expected_status_code = 400
    else:
        pdnd_accept = 'true'
        expected_status_code = 202

    context.pdnd_autocertification_response = requests.put(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.onboarding.consent}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token_io}',
        },
        json={'initiativeId': context.initiative_id,
              'pdndAccept': pdnd_accept,
              'selfDeclarationList': [
                  {
                      '_type': 'boolean',
                      'code': '1',
                      'accepted': 'true'
                  }]
              },
        timeout=settings.default_timeout
    )
    assert context.pdnd_autocertification_response.status_code == expected_status_code


@given('the merchant is {is_qualified}')
def step_merchant_qualified(context, is_qualified):
    # Merchant qualification still needs to be implemented
    if is_qualified == 'qualified':
        return True
    else:
        return True


@given('the citizen {citizen_name} enrolls a random card')
def step_card_enroll(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.card = fake_pan()
    card_enroll(fc=context.citizens_fc[citizen_name], pan=context.card, initiative_id=context.initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_io,
                 initiative_id=context.initiative_id, field='status', tries=3, delay=3,
                 message='Card not enrolled')


@given('the citizen {citizen_name} enrolls a random iban')
def step_iban_enroll(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.iban = fake_iban('00000')
    iban_enroll(fc=context.citizens_fc[citizen_name], iban=context.iban, initiative_id=context.initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_io,
                 initiative_id=context.initiative_id, field='status', tries=3, delay=3,
                 message='IBAN not enrolled')
