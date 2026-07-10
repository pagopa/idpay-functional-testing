from hashlib import sha256

from behave import given
from behave import then
from behave import when

from api.idpay import get_initiative_statistics
from api.idpay import get_initiative_statistics_merchant_portal
from api.idpay import get_onboardings_list
from api.idpay import timeline
from api.idpay import wallet
from api.onboarding_io import save_onboarding
from api.onboarding_io import status_onboarding
from conf.configuration import secrets
from conf.configuration import settings
from util.dataset_utility import fake_iban
from util.dataset_utility import fake_pan
from util.onboarding_utilities import build_self_declaration_list_payload_by_initiative, \
    build_boolean_self_declaration_list_payload
from util.onboarding_utilities import retry_io_onboarding
from util.utility import card_enroll
from util.utility import check_statistics
from util.utility import expect_wallet_counters
from util.utility import get_io_token
from util.utility import get_selfcare_token
from util.utility import iban_enroll
from util.utility import onboard_one_random_merchant
from util.utility import retry_merchant_statistics
from util.utility import retry_timeline
from util.utility import retry_wallet

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses
timeline_operations = settings.IDPAY.endpoints.timeline.operations

@given('the citizen {citizen_name} onboarded')
@given('the citizen {citizen_name} is onboard')
@given('the citizen {citizen_name} is onboarded')
def step_named_citizen_onboard(context, citizen_name):
    perform_full_onboarding(context=context, citizen_name=citizen_name)
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='OK')


@given('the citizen {citizen_name} onboards and waits for ranking')
@when('the citizen {citizen_name} onboards and waits for ranking')
def step_named_citizen_joins_ranking(context, citizen_name):
    perform_full_onboarding(context=context, citizen_name=citizen_name)
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='ON_EVALUATION')


@given('{citizens} onboard in order and wait for ranking')
@then('{citizens} onboard in order and wait for ranking')
def step_citizens_join_ranking(context, citizens):
    citizens = citizens.split()
    for c in citizens:
        perform_full_onboarding(context=context, citizen_name=c)
        step_check_onboarding_status(context=context, citizen_name=c, status='ON_EVALUATION')


@then('{citizens} are elected')
def step_check_citizens_correct_election(context, citizens):
    citizens = citizens.split()
    for c in citizens:
        step_check_onboarding_status(context=context, citizen_name=c, status='ELECTED')

    check_statistics(organization_id=context.organization_id,
                     initiative_id=context.initiative_id,
                     old_statistics=context.base_statistics,
                     onboarded_citizen_count_increment=len(citizens),
                     accrued_rewards_increment=0,
                     skip_trx_check=True)
    context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                        initiative_id=context.initiative_id).json()


@given('the citizen {citizen_name} is suspended')
@then('the citizen {citizen_name} is suspended')
def step_named_citizen_suspension(context, citizen_name):
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='SUSPENDED')


@then('the citizen {citizen_name} is readmitted')
def step_named_citizen_suspension(context, citizen_name):
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='READMITTED')


@given('the citizen {citizen_name} is not onboard')
def step_citizen_not_onboard(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.save_onboarding_response = save_onboarding(token=token_io, initiative_id=context.initiative_id,
                                                        pdnd_accept=False)
    check_statistics(organization_id=context.organization_id,
                     initiative_id=context.initiative_id,
                     old_statistics=context.base_statistics,
                     onboarded_citizen_count_increment=0,
                     accrued_rewards_increment=0,
                     skip_trx_check=True)


@then('the citizen {citizen_name} is still waiting for ranking')
@then('the citizen {citizen_name} is waiting for ranking')
def step_named_citizen_suspension(context, citizen_name):
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='ON_EVALUATION')


@given('the citizen {citizen_name} tries to onboard')
@when('the citizen {citizen_name} tries to onboard')
def step_citizen_tries_to_onboard(context, citizen_name):
    res = perform_full_onboarding(context=context, citizen_name=citizen_name)

@when('the first citizen of {citizens_names} onboards')
@given('the first citizen of {citizens_names} onboards')
def step_family_member_onboards(context, citizens_names):
    citizens = citizens_names.split()
    step_citizen_tries_to_onboard(context=context, citizen_name=citizens[0])


@given('the first citizen of {citizens_names} onboards and waits for ranking')
def step_family_member_onboards_ranking(context, citizens_names):
    citizens = citizens_names.split()
    step_citizen_tries_to_onboard(context=context, citizen_name=citizens[0])
    step_check_onboarding_status(context=context, citizen_name=citizens[0], status='ON_EVALUATION')
    citizens.pop(0)
    for c in citizens:
        step_check_onboard_not_found(context, c)


def step_check_onboard_not_found(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = status_onboarding(token_io, context.initiative_id)
    assert res.status_code == 404

@when('the citizen {citizen_name} tries to onboard the initiative {initiative_name}')
def step_citizen_tries_to_onboard_named_initiative(context, citizen_name, initiative_name):
    context.initiative_id = secrets.initiatives[initiative_name]['id']
    context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                        initiative_id=context.initiative_id).json()
    token_io = get_io_token(context.citizens_fc[citizen_name])

    multi_consent_isee_value = getattr(context, "multi_consent_isee_value", "1")

    self_declaration_list = build_self_declaration_list_payload_by_initiative(
        initiative_name,
        multi_consent_isee_value=multi_consent_isee_value
    )

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        self_declaration_list=self_declaration_list
    )


@given('the citizen {citizen_name} tries to accept terms and conditions')
@when('the citizen {citizen_name} tries to accept terms and conditions')
@when('the citizen {citizen_name} tries to accept terms and conditions again')
def step_citizen_tries_to_accept_terms_and_conditions(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.save_onboarding_response = save_onboarding(token=token_io, initiative_id=context.initiative_id)

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

@given('the citizen {citizen_name} saves PDND consent not correctly')
def step_save_pdnd_consent_not_correctly(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    confirmed_tos = context.confirmed_tos.get(citizen_name, True) if 'confirmed_tos' in context else True

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        confirmedTos=confirmed_tos,
        pdnd_accept=False
    )
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='KO')

@then('the citizen onboarding failed because {reason_ko}')
@then('the latest saving of consent failed because {reason_ko}')
@given('the latest accept terms and conditions failed for {reason_ko}')
@then('the latest accept terms and conditions failed for {reason_ko}')
def step_check_save_onboarding_failed(context, reason_ko):
    reason_ko = reason_ko.upper()

    if reason_ko == 'THE CITIZEN DID NOT ACCEPT T&C':
        assert context.save_onboarding_response.status_code == 500
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_TOS_NOT_CONFIRMED'
    elif reason_ko == 'THE CONSENT WAS DENIED BY THE CITIZEN':
        assert context.save_onboarding_response.status_code == 403
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_PDND_CONSENT_DENIED'
    elif reason_ko == 'THE CITIZEN INSERTED THE WRONG VALUE':
        assert context.save_onboarding_response.status_code == 403
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_SELF_DECLARATION_NOT_VALID'
    elif reason_ko == 'THE CITIZEN INSERTED MISMATCH VALUE':
        assert context.save_onboarding_response.status_code == 500
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_EMAIL_NOT_MATCHED'
    elif reason_ko == 'BUDGET TERMINATED':
        assert context.save_onboarding_response.status_code == 403
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_BUDGET_EXHAUSTED'
    elif reason_ko == 'USER UNSUBSCRIBED':
        assert context.save_onboarding_response.status_code == 403
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_USER_UNSUBSCRIBED'
    elif reason_ko == 'ONBOARDING PERIOD ENDED':
        assert context.save_onboarding_response.status_code == 403
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_INITIATIVE_ENDED'
    elif reason_ko == 'UNSATISFIED REQUIREMENTS':
        assert context.save_onboarding_response.status_code == 403
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_UNSATISFIED_REQUIREMENTS'
    elif reason_ko == 'INITIATIVE NOT FOUND':
        assert context.save_onboarding_response.status_code == 404
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_INITIATIVE_NOT_FOUND'
    else:
        assert False, 'Uncovered fail reason'


@then('the onboard of {citizen_name} is {status}')
@given('the onboard of {citizen_name} is {status}')
def step_check_onboarding_status(context, citizen_name, status):
    skip_statistics_check = False
    curr_onboarded_citizen_count_increment = 0

    status = status.upper()
    token_io = get_io_token(context.citizens_fc[citizen_name])
    res = status_onboarding(token_io, context.initiative_id)
    assert res.status_code == 200

    if status == 'KO':
        expected_status = f'ONBOARDING_{status}'
        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
                            message=f'Citizen onboard not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0
        res = wallet(initiative_id=context.initiative_id, token=token_io)
        assert res.status_code == 404
        res = timeline(initiative_id=context.initiative_id, token=token_io)
        assert res.status_code == 404
        assert res.json()['code'] == 'TIMELINE_USER_NOT_FOUND'

    elif status == 'SUSPENDED':
        expected_status = status
        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
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
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
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
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
                            message=f'Citizen onboard not {status}'
                            )
        retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_io,
                     initiative_id=context.initiative_id, field='status', tries=10, delay=3)
        retry_timeline(expected=timeline_operations.onboarding, request=timeline, num_required=1, token=token_io,
                       initiative_id=context.initiative_id, field='operationType', tries=10, delay=3,
                       message='Not onboard')
        expect_wallet_counters(expected_amount=context.initiative_settings['budget_per_citizen'],
                               expected_accrued=0,
                               token=token_io,
                               initiative_id=context.initiative_id)
        curr_onboarded_citizen_count_increment = 1

    elif status == 'UNSUBSCRIBED':
        expected_status = status

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
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
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
                            message=f'Citizen not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0

    elif status == 'ELECTED':
        expected_status = f'ONBOARDING_OK'

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
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
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
                            message=f'Citizen onboard not {status}'
                            )
        skip_statistics_check = False

    elif status == 'DEMANDED':
        expected_status = status

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
                            message=f'Citizen onboard not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0

    elif status == 'OK AFTER DEMANDED':
        expected_status = f'ONBOARDING_OK'

        retry_io_onboarding(expected=expected_status, request=status_onboarding, token=token_io,
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
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
                            initiative_id=context.initiative_id, field='status', tries=50, delay=0.1,
                            message=f'Citizen onboard not {status}'
                            )
        curr_onboarded_citizen_count_increment = 0

    else:
        assert False, 'Unexpected status'

    if not skip_statistics_check:
        check_statistics(organization_id=context.organization_id,
                         initiative_id=context.initiative_id,
                         old_statistics=context.base_statistics,
                         onboarded_citizen_count_increment=curr_onboarded_citizen_count_increment,
                         accrued_rewards_increment=0,
                         skip_trx_check=True)
        context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                            initiative_id=context.initiative_id).json()


@then('the onboards of {citizens_names} are {status}')
@given('the onboards of {citizens_names} are {status}')
def step_check_onboarding_citizens_status(context, citizens_names, status):
    citizens = citizens_names.split()
    for c in citizens:
        step_check_onboarding_status(context=context, citizen_name=c, status=status)


@when('the citizen {citizen_name} inserts self-declared criteria')
def step_insert_self_declared_criteria(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    self_declaration_list = build_self_declaration_list_payload_by_initiative(context.initiative_name)

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        self_declaration_list=self_declaration_list
    )
    assert context.save_onboarding_response.status_code == 202


@when('the citizen {citizen_name} tries to save PDND consent {correctness}')
def step_try_to_save_pdnd_consent(context, citizen_name, correctness):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    pdnd_accept = correctness != 'not correctly'
    confirmed_tos = context.confirmed_tos.get(citizen_name, False) if 'confirmed_tos' in context else False

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
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


@given('the random merchant {merchant_name} is onboard')
def step_merchant_random_onboard(context, merchant_name):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    curr_merchant_info = onboard_one_random_merchant(initiative_id=context.initiative_id,
                                                     institution_selfcare_token=institution_token)
    context.merchants[merchant_name] = curr_merchant_info

    context.base_merchants_statistics[merchant_name] = retry_merchant_statistics(
        merchant_id=curr_merchant_info['id'],
        initiative_id=context.initiative_id)


@given('the citizen {citizen_name} enrolls a random card')
def step_card_enroll(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.card = fake_pan()
    card_enroll(fc=context.citizens_fc[citizen_name], pan=context.card, initiative_id=context.initiative_id)
    retry_wallet(expected=wallet_statuses.not_refundable_only_instrument, request=wallet, token=token_io,
                 initiative_id=context.initiative_id, field='status', tries=3, delay=3)


@given('the citizen {citizen_name} enrolls a random iban')
def step_iban_enroll(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.iban = fake_iban('00000')
    iban_enroll(fc=context.citizens_fc[citizen_name], iban=context.iban, initiative_id=context.initiative_id)
    retry_wallet(expected=wallet_statuses.refundable, request=wallet, token=token_io,
                 initiative_id=context.initiative_id, field='status', tries=3, delay=3)


@given('citizens {citizens_names} are invited on the initiative with whitelist')
def step_check_citizens_invited_whitelist_initiative(context, citizens_names):
    citizens_names = citizens_names.split()

    institution_selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    response = get_onboardings_list(selfcare_token=institution_selfcare_token,
                                    initiative_id=context.initiative_id)

    assert response.status_code == 200
    assert len(citizens_names) == response.json()['totalElements']

    invited_citizens = response.json()['content']

    for citizen_name in citizens_names:
        citizen_fc = context.citizens_fc[citizen_name]

        is_present = False
        for invited_citizen in invited_citizens:
            if citizen_fc == invited_citizen['beneficiary']:
                is_present = True

        assert is_present

        step_check_onboarding_status(context=context,
                                     citizen_name=citizen_name,
                                     status='INVITED')


@when('the citizen {citizen_name} onboards on initiative with whitelist')
@given('the citizen {citizen_name} onboards on initiative with whitelist')
def step_citizen_tries_to_onboard_whitelist(context, citizen_name):
    perform_full_onboarding(context=context, citizen_name=citizen_name)

@when('the citizen {citizen_name} tries to onboard on initiative with whitelist')
def step_citizen_tries_to_onboard_whitelist(context, citizen_name):
    perform_full_onboarding(context=context, citizen_name=citizen_name)


@then('the latest check of prerequisites failed because {reason_ko}')
def step_check_latest_prerequisites_failed(context, reason_ko):
    reason_ko = reason_ko.upper()

    if reason_ko == 'THE CITIZEN IS NOT IN WHITELIST':
        assert context.save_onboarding_response.status_code == 403
        assert context.save_onboarding_response.json()['code'] == 'ONBOARDING_USER_NOT_IN_WHITELIST'


@when('the invited citizen tries to onboard on initiative with whitelist')
def step_invited_citizen_tries_to_onboard(context):
    fc_citizen_whitelist = secrets.fc_citizen_whitelist
    token_io = get_io_token(fc_citizen_whitelist)

    context.save_onboarding_response = save_onboarding(token=token_io, initiative_id=context.initiative_id)

@given('the citizen {citizen_name} selects ISEE type "{isee_type}"')
def step_select_isee_type(context, citizen_name, isee_type):
    mapping = {
        "under_25000": "1",
        "over_25000": "2",
        "not_declared": "3",
    }

    context.multi_consent_isee_value = mapping[isee_type]

def perform_full_onboarding(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])

    multi_consent_isee_value = getattr(context, "multi_consent_isee_value", "1")

    self_declaration_list = build_self_declaration_list_payload_by_initiative(
        context.initiative_name,
        multi_consent_isee_value=multi_consent_isee_value
    ) if 'multi_consent_isee_value' in context else None

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        self_declaration_list=self_declaration_list
    )

    assert context.save_onboarding_response.status_code == 202
    return context.save_onboarding_response


@when('the citizen {citizen_name} filled out mismatching email')
def step_try_to_insert_mismatch_email(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])

    context.save_onboarding_response = save_onboarding(
        token=token_io,
        initiative_id=context.initiative_id,
        user_mail_confirmation="mismatched_email@email.com"
    )