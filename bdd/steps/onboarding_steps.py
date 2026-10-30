import time
from hashlib import sha256

from behave import given
from behave import then
from behave import when

from api.idpay import get_initiative_statistics
from api.idpay import get_initiative_statistics_merchant_portal
from api.idpay import timeline
from api.idpay import wallet
from api.onboarding_io import save_onboarding
from api.onboarding_io import status_onboarding
from conf.configuration import secrets
from conf.configuration import settings
from util.onboarding_utilities import build_boolean_self_declaration_list_payload
from util.onboarding_utilities import build_self_declaration_list_payload_by_initiative
from util.onboarding_utilities import retry_io_onboarding
from util.utility import check_statistics
from util.utility import expect_wallet_counters
from util.utility import get_io_token
from util.utility import retry_timeline
from util.utility import retry_wallet

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses
timeline_operations = settings.IDPAY.endpoints.timeline.operations


@given('the onboard of {citizen_name} becomes OK within {timeout_seconds} seconds')
@then('the onboard of {citizen_name} becomes OK within {timeout_seconds} seconds')
def step_wait_for_onboarding_ok(context, citizen_name, timeout_seconds):
    timeout_seconds = int(timeout_seconds)
    onboarding_deadline = time.monotonic() + timeout_seconds
    token_io = get_io_token(context.citizens_fc[citizen_name])
    retry_io_onboarding(
        expected='ONBOARDING_OK',
        request=status_onboarding,
        token=token_io,
        initiative_id=context.initiative_id,
        field='status',
        tries=timeout_seconds * 2,
        delay=0.5,
        message=f'Citizen onboard not OK within {timeout_seconds} seconds'
    )
    step_check_onboarding_status(
        context=context,
        citizen_name=citizen_name,
        status='OK',
        statistics_deadline=onboarding_deadline
    )


@given('the citizen {citizen_name} tries to onboard')
@when('the citizen {citizen_name} tries to onboard')
def step_citizen_tries_to_onboard(context, citizen_name):
    res = perform_full_onboarding(context=context, citizen_name=citizen_name)


@given("the citizen {citizen_name} tries to onboard the initiative")
@when("the citizen {citizen_name} tries to onboard the initiative")
@given('the citizen {citizen_name} tries to onboard the initiative {initiative_name}')
@when('the citizen {citizen_name} tries to onboard the initiative {initiative_name}')
def step_citizen_tries_to_onboard_named_initiative(context, citizen_name, initiative_name=None):
    if initiative_name is None:
        initiative_name = context.initiative_name
    else:
        context.initiative_name = initiative_name
        context.initiative_id = secrets.initiatives[initiative_name]["id"]

    if "organization_id" in secrets.initiatives[initiative_name]:
        context.organization_id = secrets.initiatives[initiative_name]["organization_id"]
    else:
        context.organization_id = secrets.organization_id
    
    context.base_statistics = get_initiative_statistics(organization_id=context.organization_id,
                                                        initiative_id=context.initiative_id).json()
    token_io = get_io_token(context.citizens_fc[citizen_name])

    multi_consent_isee_value = getattr(context, 'multi_consent_isee_value', '1')

    self_declaration_list = build_self_declaration_list_payload_by_initiative(
        initiative_name,
        multi_consent_isee_value=multi_consent_isee_value
    )

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        self_declaration_list=self_declaration_list
    )


@when('the citizen {citizen_name} tries to onboard on nonexistent initiative')
@when('the citizen {citizen_name} tries to accept terms and conditions on a nonexistent initiative')
def step_citizen_tries_to_accept_terms_and_conditions_nonexistent_initiative(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    initiative_id_non_existent = sha256(f'{citizen_name}'.encode()).hexdigest().lower()[:24]
    context.save_onboarding_response = save_onboarding(token=token_io, initiative_id=initiative_id_non_existent)

@given('the citizen {citizen_name} accepts terms and conditions')
def step_citizen_accepts_tos(context, citizen_name):
    if 'confirmed_tos' not in context:
        context.confirmed_tos = {}
    context.confirmed_tos[citizen_name] = True

@when('the citizen {citizen_name} tries to insert wrong value in self-declared criteria')
def step_try_to_insert_self_declared_criteria(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])


    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        self_declaration_list= build_boolean_self_declaration_list_payload(self_declaration_accepted=False)
    )


@then('the citizen onboarding failed because {reason_ko}')
@then('the latest saving of consent failed because {reason_ko}')
@given('the latest accept terms and conditions failed for {reason_ko}')
@then('the latest accept terms and conditions failed for {reason_ko}')
def step_check_save_onboarding_failed(context, reason_ko):
    reason_ko = reason_ko.upper()

    if reason_ko == 'THE CITIZEN DID NOT ACCEPT T&C':
        expected_status_code = 500
        expected_status = 'ONBOARDING_TOS_NOT_CONFIRMED'
    elif reason_ko == 'THE CONSENT WAS DENIED BY THE CITIZEN':
        expected_status_code = 403
        expected_status = 'ONBOARDING_PDND_CONSENT_DENIED'
    elif reason_ko == 'THE CITIZEN INSERTED THE WRONG VALUE':
        expected_status_code = 403
        expected_status = 'ONBOARDING_SELF_DECLARATION_NOT_VALID'
    elif reason_ko == 'THE CITIZEN INSERTED MISMATCH VALUE':
        expected_status_code = 500
        expected_status = 'ONBOARDING_EMAIL_NOT_MATCHED'
    elif reason_ko == 'BUDGET TERMINATED':
        expected_status_code = 403
        expected_status = 'ONBOARDING_BUDGET_EXHAUSTED'
    elif reason_ko == 'USER UNSUBSCRIBED':
        expected_status_code = 403
        expected_status = 'ONBOARDING_USER_UNSUBSCRIBED'
    elif reason_ko == 'ONBOARDING PERIOD ENDED':
        expected_status_code = 403
        expected_status = 'ONBOARDING_INITIATIVE_ENDED'
    elif reason_ko == 'UNSATISFIED REQUIREMENTS':
        expected_status_code = 403
        expected_status = 'ONBOARDING_UNSATISFIED_REQUIREMENTS'
    elif reason_ko == 'INITIATIVE NOT FOUND':
        expected_status_code = 404
        expected_status = 'ONBOARDING_INITIATIVE_NOT_FOUND'
    elif reason_ko == 'INITIATIVE NOT STARTED':
        expected_status_code = 403
        expected_status = 'ONBOARDING_INITIATIVE_NOT_STARTED'
    elif reason_ko == 'INITIATIVE ALREADY ENDED':
        expected_status_code = 403
        expected_status = 'ONBOARDING_INITIATIVE_ALREADY_ENDED'
    elif reason_ko == 'INITIATIVE BUDGET EXHAUSTED':
        expected_status_code = 403
        expected_status = 'ONBOARDING_BUDGET_EXHAUSTED'
    elif reason_ko == 'INITIATIVE NOT PUBLISHED':
        expected_status_code = 403
        expected_status = 'ONBOARDING_INITIATIVE_STATUS_NOT_PUBLISHED'
    else:
        assert False, 'Uncovered fail reason'

    assert context.save_onboarding_response.status_code == expected_status_code, (
        'Unexpected onboarding response, '
        f'status code: {context.save_onboarding_response.status_code},'
        f'response body: {context.save_onboarding_response.text}'
    )
    assert context.save_onboarding_response.json()['code'] == expected_status, (
        'Unexpected onboarding response, '
        f'status code: {context.save_onboarding_response.status_code},'
        f'response body: {context.save_onboarding_response.text}'
    )

@then('the onboard of {citizen_name} is in error with value ONBOARDING_UNSATISFIED_REQUIREMENTS')
def step_onboarding_unsatisfied_requirements(context, citizen_name):
    expected_status = 'ONBOARDING_UNSATISFIED_REQUIREMENTS'
    max_retries = 50
    retry_delay = 5
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = None
    for attempt in range(max_retries + 1):
        res = status_onboarding(token_io, context.initiative_id)
        if res.json().get('code') == expected_status:
            break

        if attempt < max_retries:
            time.sleep(retry_delay)

    assert res is not None and res.json().get('code') == expected_status, (
        f'Onboarding status for {citizen_name} did not become {expected_status} '
        f'after {max_retries} retries; '
        f'last response: {res.status_code} {res.text}'
    )


@then('the onboard of {citizen_name} is {status}')
@given('the onboard of {citizen_name} is {status}')
def step_check_onboarding_status(context, citizen_name, status, statistics_deadline=None):
    skip_statistics_check = False
    curr_onboarded_citizen_count_increment = 0

    status = status.upper()
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = status_onboarding(token_io, context.initiative_id)
    assert res.status_code != 500, f'Unexpected onboarding status response for {citizen_name}: {res.status_code} {res.text}'

    if status == 'KO':
        expected_status = f'ONBOARDING_{status}'
        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0
        res = wallet(initiative_id=context.initiative_id, token=token_io)
        assert res.status_code == 404, f'Wallet should be absent for {citizen_name} when onboarding is KO; got {res.status_code} {res.text}'
        res = timeline(initiative_id=context.initiative_id, token=token_io)
        assert res.status_code == 404, f'Timeline should be absent for {citizen_name} when onboarding is KO; got {res.status_code} {res.text}'
        assert res.json()['code'] == 'TIMELINE_USER_NOT_FOUND', f'Unexpected timeline code for {citizen_name}: {res.text}'

    elif status == 'SUSPENDED':
        expected_status = status
        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        retry_wallet(expected=wallet_statuses.suspended, request=wallet, token=token_io,
                     initiative_id=context.initiative_id, field='status', tries=3, delay=3)
        retry_timeline(expected=timeline_operations.suspended, request=timeline, num_required=1, token=token_io,
                       initiative_id=context.initiative_id, field='operationType', tries=10, delay=3,
                       message='Not suspended')
        curr_onboarded_citizen_count_increment = 0

    elif status == 'READMITTED':
        expected_status = 'ONBOARDING_OK'
        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_io,
                     initiative_id=context.initiative_id, field='status', tries=3, delay=3)
        retry_timeline(expected=timeline_operations.readmitted, request=timeline, num_required=1, token=token_io,
                       initiative_id=context.initiative_id, field='operationType', tries=10, delay=3,
                       message='Not readmitted')
        curr_onboarded_citizen_count_increment = 0

    elif status == 'OK':
        expected_status = f'ONBOARDING_{status}'

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        retry_timeline(expected=timeline_operations.onboarding, request=timeline, num_required=1, token=token_io,
                       initiative_id=context.initiative_id, field='operationType', tries=10, delay=3,
                       message='Not onboard')
        curr_onboarded_citizen_count_increment = 1

    elif status == 'UNSUBSCRIBED':
        expected_status = "ONBOARDING_USER_NOT_ONBOARDED"

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='code', tries=62, delay=5,
                            message=f'Citizen not {status}')
        retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token_io,
                     initiative_id=context.initiative_id, field='status', tries=3, delay=3)
        retry_timeline(expected=timeline_operations.unsubscribed, request=timeline, num_required=1, token=token_io,
                       initiative_id=context.initiative_id, field='operationType', tries=10, delay=3,
                       message='Not unsubscribed')
        curr_onboarded_citizen_count_increment = 0

    elif status == 'ON_EVALUATION':
        expected_status = status

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0

    elif status == 'ELECTED':
        expected_status = f'ONBOARDING_OK'

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_io,
                     initiative_id=context.initiative_id, field='status', tries=3, delay=3)
        retry_timeline(expected=timeline_operations.onboarding, request=timeline, num_required=1, token=token_io,
                       initiative_id=context.initiative_id, field='operationType', tries=10, delay=3,
                       message='Not onboard')
        expect_wallet_counters(expected_amount=context.initiative_settings['budget_per_citizen'],
                               expected_accrued=0,
                               token=token_io,
                               initiative_id=context.initiative_id)
        skip_statistics_check = True

    elif status == 'NOT ELIGIBLE':
        expected_status = 'ELIGIBLE_KO'

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        skip_statistics_check = False

    elif status == 'DEMANDED':
        expected_status = status

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0

    elif status == 'OK AFTER DEMANDED':
        expected_status = f'ONBOARDING_OK'

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}')
        retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_io,
                     initiative_id=context.initiative_id, field='status', tries=3, delay=3)
        retry_timeline(expected=timeline_operations.onboarding, request=timeline, num_required=1, token=token_io,
                       initiative_id=context.initiative_id, field='operationType', tries=10, delay=3,
                       message='Not onboard')

        curr_onboarded_citizen_count_increment = 0

    elif status == 'INVITED':
        expected_status = status

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0

    elif status == 'FAMILY JOINED':
        expected_status = "ONBOARDING_FAMILY_UNIT_ALREADY_JOINED"

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='code', tries=62, delay=5,
                            message=f'Citizen onboard not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0
        skip_statistics_check = True

    else:
        assert False, f'Unexpected onboarding status {status} for citizen {citizen_name} in initiative {context.initiative_id}'

    if not skip_statistics_check:
        check_statistics(organization_id=context.organization_id,
                         initiative_id=context.initiative_id,
                         old_statistics=context.base_statistics,
                         onboarded_citizen_count_increment=curr_onboarded_citizen_count_increment,
                         accrued_rewards_increment=0,
                         skip_trx_check=True,
                         deadline=statistics_deadline)
        context.base_statistics = get_initiative_statistics(organization_id=context.organization_id,
                                                            initiative_id=context.initiative_id).json()


@then('the wallet of {citizen_name} is refundable with {budget} euros budget')
def step_check_initial_wallet(context, citizen_name, budget):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_io,
                 initiative_id=context.initiative_id, field='status', tries=180, delay=1)
    expect_wallet_counters(expected_amount=int(budget),
                           expected_accrued=0,
                           token=token_io,
                           initiative_id=context.initiative_id)


@then('the onboards of {citizens_names} are {status}')
@given('the onboards of {citizens_names} are {status}')
def step_check_onboarding_citizens_status(context, citizens_names, status):
    citizens = citizens_names.split()
    for c in citizens:
        step_check_onboarding_status(context=context, citizen_name=c, status=status)


@when('the citizen {citizen_name} tries to save PDND consent {correctness}')
def step_try_to_save_pdnd_consent(context, citizen_name, correctness):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    pdnd_accept = correctness != 'not correctly'
    confirmed_tos = context.confirmed_tos.get(citizen_name, False) if 'confirmed_tos' in context else False
    multi_consent_isee_value = getattr(context, 'multi_consent_isee_value', '1')

    self_declaration_list = build_self_declaration_list_payload_by_initiative(
        initiative_name=context.initiative_name,
        multi_consent_isee_value=multi_consent_isee_value
    )

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        self_declaration_list=self_declaration_list,
        confirmedTos=confirmed_tos,
        pdnd_accept=pdnd_accept
    )

@given('the merchant {merchant_name} is {is_qualified}')
def step_merchant_qualified(context, merchant_name, is_qualified):
    if is_qualified == 'qualified':
        curr_merchant_info = secrets.merchants[f'merchant_{merchant_name}']
        context.base_merchants_statistics[merchant_name] = get_initiative_statistics_merchant_portal(
            merchant_id=curr_merchant_info['id'],
            initiative_id=context.initiative_id).json()
    else:
        curr_merchant_info = {
            'id': 'UNQUALIFIED',
            'iban': 'UNQUALIFIED',
            'fiscal_code': 'UNQUALIFIED'
        }

    context.merchants[merchant_name] = curr_merchant_info


@given('the citizen {citizen_name} selects ISEE type "{isee_type}"')
def step_select_isee_type(context, citizen_name, isee_type):
    mapping = {
        'under_25000': '1',
        'over_25000': '2',
        'not_declared': '3',
    }

    context.multi_consent_isee_value = mapping[isee_type]

def perform_full_onboarding(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])

    multi_consent_isee_value = getattr(context, 'multi_consent_isee_value', '1')

    self_declaration_list = build_self_declaration_list_payload_by_initiative(
        context.initiative_name,
        multi_consent_isee_value=multi_consent_isee_value
    ) if 'multi_consent_isee_value' in context else None

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        self_declaration_list=self_declaration_list
    )

    assert context.save_onboarding_response.status_code == 202, (
        f'Onboarding failed: {context.save_onboarding_response.status_code} {context.save_onboarding_response.text}'
    )
    return context.save_onboarding_response


@when('the citizen {citizen_name} filled out mismatching email')
def step_try_to_insert_mismatch_email(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        user_mail_confirmation='mismatched_email@email.com'
    )


@when('the citizen {citizen_name} onboards the initiative {initiative_name} without an email')
@when('the citizen {citizen_name} onboards the initiative without an email')
def step_try_to_insert_mismatch_email(context, citizen_name, initiative_name=None):
    if initiative_name is None:
        initiative_name = context.initiative_name
    
    context.initiative_id = secrets.initiatives[initiative_name]['id']
    context.base_statistics = get_initiative_statistics(organization_id=context.organization_id,
                                                        initiative_id=context.initiative_id).json()
    token_io = get_io_token(context.citizens_fc[citizen_name])

    multi_consent_isee_value = getattr(context, 'multi_consent_isee_value', '1')

    self_declaration_list = build_self_declaration_list_payload_by_initiative(
        initiative_name,
        multi_consent_isee_value=multi_consent_isee_value
    )

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        self_declaration_list=self_declaration_list,
        user_mail='',
        user_mail_confirmation='',
    )

    assert context.save_onboarding_response.status_code == 202, (
        f'Onboarding failed: {context.save_onboarding_response.status_code} {context.save_onboarding_response.text}'
    )


@given('the citizen {citizen_name} has not payed Canone TV')
def step_citizen_has_not_payed_canone_tv(context, citizen_name):
    assert False, 'to be implemented'
