from hashlib import sha256

from behave import given
from behave import then
from behave import when

from api.idpay import get_initiative_statistics
from api.idpay import get_onboardings_list
from api.idpay import get_initiative_statistics_merchant_portal
from api.idpay import timeline
from api.idpay import wallet
from api.onboarding_io import accept_terms_and_conditions
from api.onboarding_io import check_prerequisites
from api.onboarding_io import pdnd_autocertification
from api.onboarding_io import status_onboarding
from conf.configuration import secrets
from conf.configuration import settings
from util.dataset_utility import fake_iban
from util.dataset_utility import fake_pan
from util.utility import card_enroll
from util.utility import check_statistics
from util.utility import expect_wallet_counters
from util.utility import get_io_token
from util.utility import get_selfcare_token
from util.utility import iban_enroll
from util.utility import onboard_one_random_merchant
from util.utility import retry_io_onboarding
from util.utility import retry_merchant_statistics
from util.utility import retry_timeline
from util.utility import retry_wallet

wallet_statuses = settings.IDPAY.endpoints.wallet.statuses
timeline_operations = settings.IDPAY.endpoints.timeline.operations


@given('the citizen {citizen_name} onboarded')
@given('the citizen {citizen_name} is onboard')
@given('the citizen {citizen_name} is onboarded')
def step_named_citizen_onboard(context, citizen_name):
    step_citizen_accept_terms_and_conditions(context=context, citizen_name=citizen_name)
    step_insert_self_declared_criteria(context=context, citizen_name=citizen_name)
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='OK')


@given('the citizen {citizen_name} onboards and waits for ranking')
@when('the citizen {citizen_name} onboards and waits for ranking')
def step_named_citizen_joins_ranking(context, citizen_name):
    step_citizen_accept_terms_and_conditions(context=context, citizen_name=citizen_name)
    step_insert_self_declared_criteria(context=context, citizen_name=citizen_name)
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='ON_EVALUATION')


@given('{citizens} onboard in order and wait for ranking')
@then('{citizens} onboard in order and wait for ranking')
def step_citizens_join_ranking(context, citizens):
    citizens = citizens.split()
    for c in citizens:
        step_citizen_accept_terms_and_conditions(context=context, citizen_name=c)
        step_insert_self_declared_criteria(context=context, citizen_name=c)
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
    step_citizen_accept_terms_and_conditions(context=context, citizen_name=citizen_name)
    step_try_to_save_pdnd_consent(context=context, citizen_name=citizen_name, correctness='not correctly')
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


@when('the citizen {citizen_name} tries to onboard')
def step_citizen_tries_to_onboard(context, citizen_name):
    step_citizen_accept_terms_and_conditions(context=context, citizen_name=citizen_name)
    step_insert_self_declared_criteria(context=context, citizen_name=citizen_name)


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
    new_context = context
    new_context.initiative_id = secrets.initiatives[initiative_name]['id']
    context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                        initiative_id=context.initiative_id).json()
    step_citizen_accept_terms_and_conditions(context=context, citizen_name=citizen_name)
    step_insert_self_declared_criteria(context=context, citizen_name=citizen_name)


@when('the citizen {citizen_name} tries to accept terms and conditions')
def step_citizen_tries_to_accept_terms_and_conditions(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.accept_tc_response = accept_terms_and_conditions(token=token_io, initiative_id=context.initiative_id)


@when('the citizen {citizen_name} tries to accept terms and conditions on a nonexistent initiative')
def step_citizen_tries_to_accept_terms_and_conditions_nonexistent_initiative(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    initiative_id_non_existent = sha256(f'{citizen_name}'.encode()).hexdigest().lower()[:24]
    context.accept_tc_response = accept_terms_and_conditions(token=token_io, initiative_id=initiative_id_non_existent)


@then('the latest accept terms and conditions failed for {reason_ko}')
def step_check_latest_accept_tc_failed(context, reason_ko):
    reason = reason_ko.upper()
    if reason == 'BUDGET TERMINATED':
        assert context.accept_tc_response.status_code == 403
        assert context.accept_tc_response.json()['code'] == 'ONBOARDING_BUDGET_EXHAUSTED'
    elif reason == 'USER UNSUBSCRIBED':
        assert context.accept_tc_response.status_code == 403
        assert context.accept_tc_response.json()['code'] == 'ONBOARDING_USER_UNSUBSCRIBED'
    elif reason == 'ONBOARDING PERIOD ENDED':
        assert context.accept_tc_response.status_code == 403
        assert context.accept_tc_response.json()['code'] == 'ONBOARDING_INITIATIVE_ENDED'
    elif reason == 'INITIATIVE NOT FOUND':
        assert context.accept_tc_response.status_code == 404
        assert context.accept_tc_response.json()['code'] == 'ONBOARDING_INITIATIVE_NOT_FOUND'
    else:
        assert False, 'Uncovered fail reason'


@given('the citizen {citizen_name} accepts terms and conditions')
def step_citizen_accept_terms_and_conditions(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.accept_tc_response = accept_terms_and_conditions(token=token_io, initiative_id=context.initiative_id)
    assert context.accept_tc_response.status_code == 204


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
                     initiative_id=context.initiative_id, field='status', tries=3, delay=3)
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
                            message=f'Citizen not {status}'
                            )
        retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token_io,
                     initiative_id=context.initiative_id, field='status', tries=3, delay=3)
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

    context.pdnd_autocertification_response = pdnd_autocertification(token=token_io,
                                                                     initiative_id=context.initiative_id)
    assert context.pdnd_autocertification_response.status_code == 202


@given('the citizen {citizen_name} saves PDND consent not correctly')
def step_try_to_save_pdnd_consent(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.pdnd_autocertification_response = pdnd_autocertification(token=token_io,
                                                                     initiative_id=context.initiative_id,
                                                                     pdnd_accept='false')
    step_check_saving_consent(context=context, reason_ko='THE CONSENT WAS DENIED BY THE CITIZEN')


@when('the citizen {citizen_name} tries to save PDND consent {correctness}')
def step_try_to_save_pdnd_consent(context, citizen_name, correctness):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    if correctness == 'not correctly':
        pdnd_accept = 'false'
    else:
        pdnd_accept = 'true'

    context.pdnd_autocertification_response = pdnd_autocertification(token=token_io,
                                                                     initiative_id=context.initiative_id,
                                                                     pdnd_accept=pdnd_accept)


@when('the citizen {citizen_name} tries to insert wrong value in self-declared criteria')
def step_try_to_insert_self_declared_criteria(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])
    context.pdnd_autocertification_response = pdnd_autocertification(token=token_io,
                                                                     initiative_id=context.initiative_id,
                                                                     self_declaration_accepted='false')


@then('the latest saving of consent failed because {reason_ko}')
def step_check_saving_consent(context, reason_ko):
    reason_ko = reason_ko.upper()
    if reason_ko == 'THE CITIZEN DID NOT ACCEPT T&C':
        assert context.latest_pdnd_autocertification_response.status_code == 403
        assert context.latest_pdnd_autocertification_response.json()['code'] == 'ONBOARDING_USER_NOT_ONBOARDED'
    elif reason_ko == 'THE CONSENT WAS DENIED BY THE CITIZEN':
        assert context.latest_pdnd_autocertification_response.status_code == 403
        assert context.latest_pdnd_autocertification_response.json()['code'] == 'ONBOARDING_PDND_CONSENT_DENIED'
    elif reason_ko == 'THE CITIZEN INSERTED THE WRONG VALUE':
        assert context.latest_pdnd_autocertification_response.status_code == 403
        assert context.latest_pdnd_autocertification_response.json()['code'] == 'ONBOARDING_SELF_DECLARATION_NOT_VALID'


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
def step_merchant_qualified(context, merchant_name):
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


@given('citizens {citizens_names} are invited on this initiative')
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


@when('the citizen {citizen_name} onboards on whitelist initiative')
@given('the citizen {citizen_name} onboards on whitelist initiative')
def step_citizen_tries_to_onboard_whitelist(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])

    accept_tc_response = accept_terms_and_conditions(token=token_io, initiative_id=context.initiative_id)
    assert accept_tc_response.status_code == 204

    check_prerequisites_response = check_prerequisites(token=token_io, initiative_id=context.initiative_id)
    assert check_prerequisites_response.status_code == 202


@when('the citizen {citizen_name} tries to onboard on whitelist initiative')
def step_citizen_tries_to_onboard_whitelist(context, citizen_name):
    token_io = get_io_token(context.citizens_fc[citizen_name])

    accept_tc_response = accept_terms_and_conditions(token=token_io, initiative_id=context.initiative_id)
    assert accept_tc_response.status_code == 204

    context.latest_check_prerequisites = check_prerequisites(token=token_io, initiative_id=context.initiative_id)


@then('the latest check of prerequisites failed because {reason_ko}')
def step_check_latest_prerequisites_failed(context, reason_ko):
    reason_ko = reason_ko.upper()

    if reason_ko == 'THE CITIZEN IS NOT IN WHITELIST':
        assert context.latest_check_prerequisites.status_code == 403
        assert context.latest_check_prerequisites.json()['code'] == 'ONBOARDING_USER_NOT_IN_WHITELIST'


@when('the invited citizen tries to onboard on whitelist initiative')
def step_invited_citizen_tries_to_onboard(context):
    fc_citizen_whitelist = secrets.fc_citizen_whitelist
    token_io = get_io_token(fc_citizen_whitelist)

    context.accept_tc_response = accept_terms_and_conditions(token=token_io, initiative_id=context.initiative_id)
