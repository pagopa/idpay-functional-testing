from behave import given
from behave import then
from behave import when
from api.idpay import get_idpay_code_status, post_idpay_code_generate, get_payment_instruments, timeline, \
    put_code_instrument, remove_payment_instrument
from conf.configuration import settings
from util.utility import get_io_token, retry_timeline

timeline_operations = settings.IDPAY.endpoints.timeline.operations


@given('the citizen {citizen_name} generates the idpay code')
@when('the citizen {citizen_name} generates the idpay code')
@when('the citizen {citizen_name} regenerates the idpay code')
def step_idpay_code_generate(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io, body={})

    assert res.status_code == 200


@given('the idpay_code is {status} for citizen {citizen_name}')
@then('the idpay_code is {status} for citizen {citizen_name}')
def step_check_idpay_code_status(context, status, citizen_name):
    status = status.upper()
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = get_idpay_code_status(token=token_io)
    assert res.status_code == 200

    if status == "ENABLED":
        assert res.json()['isIdPayCodeEnabled'] is True
    elif status == "NOT ENABLED":
        assert res.json()['isIdPayCodeEnabled'] is False


@when('the citizen {citizen_name} enrolls the CIE')
@given('the citizen {citizen_name} enrolls the CIE')
def step_citizen_enroll_cie(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io,
                                   body={'initiativeId': context.initiative_id})

    assert res.status_code == 200
    step_check_idpay_code_status(context=context, status='enabled', citizen_name=citizen_name)


@when('the citizen {citizen_name} enables the CIE')
def step_citizen_enable_cie(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = put_code_instrument(token=token_io, initiative_id=context.initiative_id)

    assert res.status_code == 200


@when('the citizen {citizen_name} tries to enable the CIE')
def step_citizen_try_enable_cie(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = put_code_instrument(token=token_io, initiative_id=context.initiative_id)

    context.latest_enabling_response = res


@then('the latest CIE enabling fails because {cause_ko}')
def step_check_latest_cie_enabling_failed(context, cause_ko):
    cause_ko = cause_ko.upper()

    if cause_ko == 'THE CODE IS MISSING':
        assert context.latest_enabling_response.status_code == 403
        assert context.latest_enabling_response.json()['code'] == 403
        assert context.latest_enabling_response.json()['message'] == 'IdpayCode must be generated'


@when('the citizen {citizen_name} tries to enroll the CIE')
def step_citizen_try_enroll_cie(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io, body={'initiativeId': context.initiative_id})

    context.latest_enrollment_response = res


@then('the latest CIE enrollment fails because {cause_ko}')
def step_check_latest_cie_enrollment_failed(context, cause_ko):
    cause_ko = cause_ko.upper()

    if cause_ko == 'THE CITIZEN IS NOT ONBOARD':
        assert context.latest_enrollment_response.status_code == 404
        assert context.latest_enrollment_response.json()['code'] == 404
        assert context.latest_enrollment_response.json()[
                   'message'] == 'The requested initiative is not active for the current user!'
    elif cause_ko == 'THE CITIZEN IS UNSUBSCRIBED':
        assert context.latest_enrollment_response.status_code == 400
        assert context.latest_enrollment_response.json()['code'] == 400
        assert context.latest_enrollment_response.json()['message'] == 'You are unsubscribed at this initiative!'


@when('the citizen {citizen_name} disables the CIE')
@given('the citizen {citizen_name} disables the CIE')
def step_citizen_try_disable_cie(context, citizen_name):
    initiative_id = context.initiative_id
    token_io = get_io_token(context.citizens_fc[citizen_name])

    res = get_payment_instruments(initiative_id=initiative_id, token=token_io)
    assert res.status_code == 200

    instrument_id = res.json()['instrumentList'][0]['instrumentId']

    res = remove_payment_instrument(initiative_id=initiative_id, token=token_io, instrument_id=instrument_id)
    assert res.status_code == 200


@given('the instrument CIE is in {status} status for citizen {citizen_name} on initiative')
@then('the instrument CIE is in {status} status for citizen {citizen_name} on initiative')
def step_check_status_instrument_cie(context, status, citizen_name):
    initiative_id = context.initiative_id
    status = status.upper()
    token_io = get_io_token(context.citizens_fc[citizen_name])

    res = get_payment_instruments(token=token_io,
                                  initiative_id=initiative_id)
    assert res.status_code == 200

    if status == 'ACTIVE':
        cie_instrument = res.json()['instrumentList'][0]
        assert cie_instrument['instrumentType'] == 'IDPAYCODE'
        assert cie_instrument['status'] == 'ACTIVE'

        retry_timeline(expected=timeline_operations.add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=1, message='Card not enrolled')

    elif status == 'ACTIVE AGAIN':
        cie_instrument = res.json()['instrumentList'][0]
        assert cie_instrument['instrumentType'] == 'IDPAYCODE'
        assert cie_instrument['status'] == 'ACTIVE'

        retry_timeline(expected=timeline_operations.add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=2, tries=50,
                       delay=1, message='Card not enrolled')

    elif status == 'DELETED':
        assert len(res.json()['instrumentList']) == 0

        retry_timeline(expected=timeline_operations.delete_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=1, message='Delete card rejected')

    elif status == 'REJECTED ADD':
        assert len(res.json()['instrumentList']) == 0

        retry_timeline(expected=timeline_operations.rejected_add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=1, message='Add card not rejected')

    elif status == 'REJECTED DELETE':
        assert len(res.json()['instrumentList']) == 0

        retry_timeline(expected=timeline_operations.rejected_delete_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=1, message='Delete card not rejected')
