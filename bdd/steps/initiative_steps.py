import datetime
import math

import pytz
from behave import given
from behave import then
from behave import when

from api.idpay import get_initiative_info
from api.idpay import get_initiative_statistics
from api.idpay import get_ranking_page
from bdd.steps.dataset_steps import step_citizen_fc_exact_or_random
from bdd.steps.onboarding_steps import step_named_citizen_onboard
from conf.configuration import secrets
from conf.configuration import settings
from util.utility import check_statistics
from util.utility import create_initiative_and_update_conf
from util.utility import get_selfcare_token
from util.utility import retry_institution_statistics


@given('the initiative is "{initiative_name}"')
def step_given_initiative_name(context, initiative_name):
    context.initiative_id = secrets.initiatives[initiative_name]['id']
    context.initiative_settings = settings.initiatives[initiative_name]
    base_context_initialization(context)


@given('the initiative id is "{initiative_id}" ("{initiative_name}")')
def step_given_initiative_id(context, initiative_id, initiative_name):
    context.initiative_id = initiative_id
    context.initiative_settings = settings.initiatives[initiative_name]
    base_context_initialization(context)


@then('the initiative counters are updated')
def step_check_initiative_statistics_updated(context):
    check_statistics(organization_id=context.organization_id, initiative_id=context.initiative_id,
                     old_statistics=context.base_statistics,
                     onboarded_citizen_count_increment=context.num_onboards,
                     accrued_rewards_increment=context.expected_accrued,
                     rewarded_trxs_increment=context.num_trx)


def base_context_initialization(context):
    context.cashback_percentage = context.initiative_settings.get('cashback_percentage')
    context.budget_per_citizen = context.initiative_settings['budget_per_citizen']
    context.fruition_start = context.initiative_settings['fruition_start']
    context.total_budget = context.initiative_settings.get('total_budget')

    context.trx_date = (datetime.datetime.now(pytz.timezone('Europe/Rome')) + datetime.timedelta(days=1)).strftime(
        settings.iso_date_format)

    context.base_statistics = retry_institution_statistics(initiative_id=context.initiative_id)
    context.base_merchants_statistics = {}

    context.transactions = {}

    context.num_new_onboards = 0
    context.citizens_fc = {}

    context.num_new_trxs = 0
    context.organization_id = secrets.organization_id

    context.trxs_per_citizen = {}
    context.accrued_per_citizen = {}
    context.total_accrued = 0

    context.merchants = {}

    context.associated_citizen = {}
    context.associated_merchant = {}

    context.citizen_isee = {}

    context.idpay_code = {}
    context.old_idpay_code = {}
    context.second_factor = {}


@given("the initiative's budget is {precision} allocated")
def step_allocate_initiative_budget(context, precision):
    i = 0
    allowable_citizens = math.floor(context.total_budget / context.budget_per_citizen)

    if precision == 'almost':
        allowable_citizens -= 1

    context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                        initiative_id=context.initiative_id).json()

    while context.base_statistics['onboardedCitizenCount'] < allowable_citizens:
        step_citizen_fc_exact_or_random(context=context, citizen_name=str(i), citizen_fc='random')
        step_named_citizen_onboard(context=context, citizen_name=str(i))
        context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                            initiative_id=context.initiative_id).json()
        i += 1

    assert context.base_statistics['onboardedCitizenCount'] == allowable_citizens


@given('a new initiative "{initiative_name}"')
def step_create_new_initiative(context, initiative_name):
    create_initiative_and_update_conf(initiative_name=initiative_name)
    step_given_initiative_name(context=context, initiative_name=initiative_name)


@when('a new whitelist initiative "{initiative_name}"')
def step_create_new_initiative_with_whitelist(context, initiative_name):
    secrets.initiatives[initiative_name] = {}
    create_initiative_and_update_conf(initiative_name=initiative_name,
                                      known_beneficiaries=context.known_beneficiaries)
    context.initiative_id = secrets.initiatives[initiative_name]['id']
    context.initiative_settings = settings.initiatives[initiative_name]


@given('the initiative is in grace period')
def step_initiative_in_grace_period(context):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = get_initiative_info(selfcare_token=institution_token, initiative_id=context.initiative_id)
    assert res.json()['general']['rankingEndDate'] < datetime.datetime.now().strftime('%Y-%m-%d')
    assert res.json()['general']['startDate'] > datetime.datetime.now().strftime('%Y-%m-%d')


@given('the initiative is in fruition period')
def step_initiative_in_grace_period(context):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = get_initiative_info(selfcare_token=institution_token, initiative_id=context.initiative_id)
    assert res.json()['general']['rankingEndDate'] <= datetime.datetime.now().strftime('%Y-%m-%d')
    assert res.json()['general']['startDate'] <= datetime.datetime.now().strftime('%Y-%m-%d')


@given('the initiative has a rank')
def step_initiative_has_a_rank(context):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = get_ranking_page(selfcare_token=institution_token, initiative_id=context.initiative_id)
    assert res.json()['rankingStatus'] == 'COMPLETED'

    for citizen in res.json()['content']:
        if citizen['beneficiaryRankingStatus'] == 'ELIGIBLE_OK':
            context.eligible_citizen = citizen['beneficiary']
        elif citizen['beneficiaryRankingStatus'] == 'ELIGIBLE_KO':
            context.not_eligible_citizen = citizen['beneficiary']
        elif citizen['beneficiaryRankingStatus'] == 'ONBOARDING_KO':
            context.not_onboard_citizen = citizen['beneficiary']

    assert context.eligible_citizen is not None
    assert context.not_eligible_citizen is not None
    assert context.not_onboard_citizen is not None
