from hashlib import sha256

from behave import given
from behave import then
from behave import when

from api.idpay import get_idpay_code_status
from api.idpay import get_payment_instruments
from api.idpay import post_idpay_code_generate
from api.idpay import put_code_instrument
from api.idpay import remove_payment_instrument
from api.idpay import timeline
from conf.configuration import settings
from util.utility import get_io_token
from util.utility import retry_payment_instrument
from util.utility import retry_timeline

timeline_operations = settings.IDPAY.endpoints.timeline.operations
instrument_types = settings.IDPAY.endpoints.wallet.instrument_type


@given('the citizen {citizen_name} generates the IDPay Code')
@when('the citizen {citizen_name} generates the IDPay Code')
def step_idpay_code_generate(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io)
    assert res.status_code == 200

    context.idpay_code = res.json()['idpayCode']


@when('the citizen {citizen_name} regenerates the IDPay Code')
def step_idpay_code_regenerate(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io)
    assert res.status_code == 200
    assert res.json()['idpayCode'] != context.idpay_code

    context.idpay_code = res.json()['idpayCode']


@given('the IDPay Code is {status} for citizen {citizen_name}')
@then('the IDPay Code is {status} for citizen {citizen_name}')
def step_check_idpay_code_status(context, status, citizen_name):
    status = status.upper()
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = get_idpay_code_status(token=token_io)
    assert res.status_code == 200

    if status == 'ENABLED':
        assert res.json()['isIdPayCodeEnabled'] is True
    elif status == 'NOT ENABLED':
        assert res.json()['isIdPayCodeEnabled'] is False


@when('the citizen {citizen_name} enrolls a new IDPay Code on the initiative')
@given('the citizen {citizen_name} enrolls a new IDPay Code on the initiative')
def step_citizen_enroll_idpay_code(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io,
                                   body={'initiativeId': context.initiative_id})

    assert res.status_code == 200
    step_check_idpay_code_status(context=context, status='enabled', citizen_name=citizen_name)


@given('the citizen {citizen_name} uses its IDPay Code on the initiative')
@when('the citizen {citizen_name} uses its IDPay Code on the initiative')
def step_citizen_enable_idpay_code(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = put_code_instrument(token=token_io, initiative_id=context.initiative_id)

    assert res.status_code == 200


@when('the citizen {citizen_name} tries to use its IDPay Code on the initiative')
def step_citizen_try_enable_idpay_code(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = put_code_instrument(token=token_io, initiative_id=context.initiative_id)

    context.latest_idpay_code_enabling_response = res


@then('the latest IDPay Code enabling fails because {cause_ko}')
def step_check_latest_idpay_code_enabling_failed(context, cause_ko):
    cause_ko = cause_ko.upper()

    if cause_ko == 'THE CODE IS MISSING':
        assert context.latest_idpay_code_enabling_response.status_code == 403
        assert context.latest_idpay_code_enabling_response.json()['code'] == 403
        assert context.latest_idpay_code_enabling_response.json()['message'] == 'IdpayCode must be generated'


@when('the citizen {citizen_name} tries to enroll a new IDPay Code on the initiative')
def step_citizen_try_enroll_idpay_code(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = post_idpay_code_generate(token=token_io, body={'initiativeId': context.initiative_id})

    context.latest_idpay_code_enabling_response = res


@then('the latest IDPay Code enrollment fails because {cause_ko}')
def step_check_latest_idpay_code_enrollment_failed(context, cause_ko):
    cause_ko = cause_ko.upper()

    if cause_ko == 'THE CITIZEN IS NOT ONBOARD':
        assert context.latest_idpay_code_enabling_response.status_code == 404
        assert context.latest_idpay_code_enabling_response.json()['code'] == 404
        assert context.latest_idpay_code_enabling_response.json()[
                   'message'] == 'The requested initiative is not active for the current user!'
    elif cause_ko == 'THE CITIZEN IS UNSUBSCRIBED':
        assert context.latest_idpay_code_enabling_response.status_code == 400
        assert context.latest_idpay_code_enabling_response.json()['code'] == 400
        assert context.latest_idpay_code_enabling_response.json()[
                   'message'] == 'You are unsubscribed at this initiative!'


@given('the citizen {citizen_name} disables the IDPay Code from the initiative')
@when('the citizen {citizen_name} disables the IDPay Code from the initiative')
def step_citizen_disable_idpay_code(context, citizen_name):
    initiative_id = context.initiative_id
    token_io = get_io_token(context.citizens_fc[citizen_name])

    res = get_payment_instruments(initiative_id=initiative_id, token=token_io)
    assert res.status_code == 200
    assert res.json()['instrumentList'] != []

    instrument_idpay_code = None
    for instrument in res.json()['instrumentList']:
        if instrument['instrumentType'] == 'IDPAYCODE':
            instrument_idpay_code = instrument

    assert instrument_idpay_code is not None
    instrument_id = instrument_idpay_code['instrumentId']

    res = remove_payment_instrument(initiative_id=initiative_id, token=token_io, instrument_id=instrument_id)
    assert res.status_code == 200


@when('the citizen {citizen_name} tries to disable the IDPay Code on the initiative')
def step_citizen_try_disable_idpay_code(context, citizen_name):
    initiative_id = context.initiative_id
    token_io = get_io_token(context.citizens_fc[citizen_name])

    res = get_payment_instruments(initiative_id=initiative_id, token=token_io)
    assert res.status_code == 200
    assert res.json()['instrumentList'] != []

    instrument_idpay_code = None
    for instrument in res.json()['instrumentList']:
        if instrument['instrumentType'] == 'IDPAYCODE':
            instrument_idpay_code = instrument

    if instrument_idpay_code is not None:
        instrument_id = instrument_idpay_code['instrumentId']
    else:
        instrument_id = sha256(f'{citizen_name}'.encode()).hexdigest().lower()[:24]

    res = remove_payment_instrument(initiative_id=initiative_id, token=token_io, instrument_id=instrument_id)
    context.latest_response_idpay_code_deactivation = res


@then('the latest IDPay Code deactivation fails because {cause_ko}')
def step_check_latest_response_idpay_code_deactivation(context, cause_ko):
    cause_ko = cause_ko.upper()

    if cause_ko == 'THE INSTRUMENT IS NOT ACTIVE':
        assert context.latest_response_idpay_code_deactivation.status_code == 404
        assert context.latest_response_idpay_code_deactivation.json()['code'] == 404
        assert context.latest_response_idpay_code_deactivation.json()[
                   'message'] == 'The selected payment instrument is not active for such user and initiative.'


@given('the instrument IDPay Code is in {status} status for citizen {citizen_name} on initiative')
@then('the instrument IDPay Code is in {status} status for citizen {citizen_name} on initiative')
def step_check_status_instrument_idpay_code(context, status, citizen_name):
    initiative_id = context.initiative_id
    status = status.upper()
    token_io = get_io_token(context.citizens_fc[citizen_name])

    if status == 'ACTIVE':
        retry_payment_instrument(expected_type=instrument_types.idpaycode, expected_status='ACTIVE',
                                 request=get_payment_instruments, token=token_io, initiative_id=initiative_id,
                                 field_type='instrumentType', field_status='status', num_required=1, tries=50, delay=2)

        retry_timeline(expected=timeline_operations.add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=2, message='Card not enrolled')

    elif status == 'ACTIVE AGAIN':
        retry_payment_instrument(expected_type=instrument_types.idpaycode, expected_status='ACTIVE',
                                 request=get_payment_instruments, token=token_io, initiative_id=initiative_id,
                                 field_type='instrumentType', field_status='status', num_required=1, tries=50, delay=2)

        retry_timeline(expected=timeline_operations.add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=2, tries=50,
                       delay=2, message='Card not enrolled')

    elif status == 'DELETED':
        retry_timeline(expected=timeline_operations.delete_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=2, message='Delete card rejected')

    elif status == 'REJECTED ADD':
        retry_timeline(expected=timeline_operations.rejected_add_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=2, message='Add card not rejected')

    elif status == 'REJECTED DELETE':
        retry_timeline(expected=timeline_operations.rejected_delete_instrument, request=timeline, token=token_io,
                       initiative_id=initiative_id, field='operationType', num_required=1, tries=50,
                       delay=2, message='Delete card not rejected')
