from behave import given
from behave import then
from behave import when

from api.idpay import get_initiative_statistics_merchant_portal
from api.idpay import obtain_merchant_test_token
from api.merchant import exchange_selfcare_token_merchant_portal
from api.merchant import get_merchant_initiatives_merchant_portal
from api.merchant import put_merchant
from api.merchant import put_onboard_merchant_initiative
from api.merchant import mock_merchant_ateco
from conf.configuration import secrets
from util.jwt_utilities import decode_jwt_payload
from util.merchant_utilities import generate_merchant_name
from util.merchant_utilities import generate_merchant_vat


@given('merchant successfully logged in SelfCare')
def step_merchant_logged_in_selfcare(context):
    context.merchant_selfcare_token = secrets.merchant_portal.selfcare_token


@when('merchant access Merchant Portal')
def step_merchant_access_merchant_portal(context):
    context.merchant_portal_token_response = exchange_selfcare_token_merchant_portal(
        context.merchant_selfcare_token
    )


@then('merchant has been successfully logged in Merchant Portal')
def step_merchant_logged_in_merchant_portal(context):
    response = context.merchant_portal_token_response
    assert response.status_code == 200, (
        f'token exchange failed: {response.status_code} {response.text}'
    )

    merchant_token = response.text.strip()
    merchant_token_payload = decode_jwt_payload(merchant_token)
    merchant_id = merchant_token_payload.get('merchant_id')
    assert merchant_id, f'merchant token does not contain merchant_id: {merchant_token_payload}'

    initiatives_response = get_merchant_initiatives_merchant_portal(
        merchant_token=merchant_token,
        merchant_id=merchant_id,
    )
    assert initiatives_response.status_code == 200, (
        'merchant token was rejected by idpay-merchant: '
        f'{initiatives_response.status_code} {initiatives_response.text}'
    )


@given('merchant {merchant_name} login through Self-Care')
def merchant_logged_in(context, merchant_name):
    fiscal_code = generate_merchant_vat()
    business_name = generate_merchant_name()
    acquirer_id = 'PAGOPA'

    put_response = put_merchant(
        fiscal_code=fiscal_code,
        vat_number=fiscal_code,
        business_name=business_name,
        acquirer_id=acquirer_id,
        iban='IT60X0542811101000000123456',
        iban_holder='Esercente di test',
        activation_date='2026-09-12T00:00:00',
    )
    assert put_response.status_code == 200, (
        'merchant creation failed: '
        f'status={put_response.status_code}, body={put_response.text}'
    )
    merchant_id = put_response.text

    response = obtain_merchant_test_token({
        'aud': 'idpay.merchant.welfare.pagopa.it',
        'uid': '83843864-f3c0-4def-badb-7f197471b72e',
        'iss': 'https://api-io.dev.cstar.pagopa.it',
        'orgId': '390cea38-f2de-4bcb-a181-d6eef99fe528',
        'orgName': 'test institution',
        'name': business_name,
        'familyName': 'test institution',
        'email': 'test@institution.com',
        'orgVAT': fiscal_code,
        'orgPartyRole': 'SUB_DELEGATE',
        'orgRole': 'admin',
        'merchantId': merchant_id,
        'acquirerId': acquirer_id,
    })
    assert response.status_code == 200, (
        'merchant token request failed: '
        f'status={response.status_code}, body={response.text}'
    )
    token = response.text

    if context.merchants is None: context.merchants = {}
    context.merchants[merchant_name] = {
        'token': token,
        'fiscalCode': fiscal_code,
        'merchantId': merchant_id,
    }


@given('merchant {merchant_name} has ATECO code {ateco}')
def step_merchant_has_ateco_code(context, merchant_name, ateco):
    mock_merchant_ateco(context.merchants [merchant_name]['fiscalCode'], ateco=ateco)


@given("merchant {merchant_name} isn't onboarded on {initiative_name}")
def step_merchant_is_not_onboarded(context, merchant_name, initiative_name):
    initiative_id = secrets.initiatives[initiative_name]['id']
    response = get_initiative_statistics_merchant_portal(
        merchant_id=context.merchants[merchant_name]['merchantId'],
        initiative_id=initiative_id
    )

    assert response.status_code == 404, (
        f'merchant is already onboarded: {response.status_code} {response.text}'
    )


@given('merchant {merchant_name} has onboarded initiative {initiative_name}')
def step_merchant_has_onboarded_initiative(context, merchant_name, initiative_name):
    initiative_id = secrets.initiatives[initiative_name]['id']
    response = put_onboard_merchant_initiative(
        selfcare_token=context.merchants[merchant_name]['token'],
        merchant_id=context.merchants[merchant_name]['merchantId'],
        initiative_id=initiative_id
    )

    assert response.status_code == 200, (
        f'merchant onboarding setup failed: {response.status_code} {response.text}'
    )


@when('merchant {merchant_name} tries to onboard the initiative {initiative_name}')
def step_merchant_tries_to_onboard_initiative(context, merchant_name, initiative_name):
    initiative_id = secrets.initiatives[initiative_name]['id']

    context.merchants[merchant_name]['onboarding_response'] = put_onboard_merchant_initiative(
        selfcare_token=context.merchants[merchant_name]['token'],
        merchant_id=context.merchants[merchant_name]['merchantId'],
        initiative_id=initiative_id
    )


@then('the onboarding attempt of merchant {merchant_name} is successfull')
def step_check_merchant_onboarding_successful(context, merchant_name):
    response = context.merchants[merchant_name]['onboarding_response']
    assert response.status_code == 200, (
        f"onboarding failed: {response.status_code} {response.text}"
    )


@then('the onboarding attempt of merchant {merchant_name} fails because not eligible')
def step_check_merchant_onboarding_not_eligible(context, merchant_name):
    response = context.merchants[merchant_name]['onboarding_response']
    assert response.status_code == 500, (
        f"onboarding did not fail as expected: {response.status_code} {response.text}"
    )
    assert response.json()['code'] == 'MERCHANT_NOT_ELIGIBLE'


@then('the onboarding attempt of merchant {merchant_name} fails because already onboarded')
def step_check_merchant_onboarding_already_onboarded(context, merchant_name):
    response = context.merchants[merchant_name]['onboarding_response']
    assert response.status_code == 500, (
        f'onboarding did not fail as expected: {response.status_code} {response.text}'
    )
    assert response.json()['code'] == 'MERCHANT_ALREDY_ONBORDED'
