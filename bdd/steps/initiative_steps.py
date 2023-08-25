import datetime
import math
import time

import pytz
from behave import given
from behave import then

from api.idpay import get_initiative_statistics
from bdd.steps.onboarding_steps import step_citizen_tries_to_onboard
from conf.configuration import secrets
from conf.configuration import settings
from util.dataset_utility import fake_fc
from util.utility import check_statistics


@given('the initiative is "{initiative_name}"')
def step_given_initiative_id(context, initiative_name):
    context.initiative_id = secrets.initiatives[initiative_name]['id']
    context.initiatives_settings = settings.initiatives[initiative_name]
    base_context_initialization(context)


@then('the initiative counters are updated')
def step_check_initiative_statistics_updated(context):
    check_statistics(organization_id=context.organization_id, initiative_id=context.initiative_id,
                     old_statistics=context.base_statistics,
                     onboarded_citizen_count_increment=context.num_onboards,
                     accrued_rewards_increment=context.expected_accrued,
                     rewarded_trxs_increment=context.num_trx)


def base_context_initialization(context):
    context.cashback_percentage = context.initiatives_settings.get('cashback_percentage')
    context.budget_per_citizen = context.initiatives_settings['budget_per_citizen']
    context.fruition_start = context.initiatives_settings['fruition_start']
    context.total_budget = context.initiatives_settings.get('total_budget')

    context.trx_date = (datetime.datetime.now(pytz.timezone('Europe/Rome')) + datetime.timedelta(days=1)).strftime(
        settings.iso_date_format)

    context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                        initiative_id=context.initiative_id).json()
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


@given("the initiative's budget is totally allocated")
def step_check_initiative_budget_allocated(context):
    allowable_citizens = math.floor(context.total_budget / context.budget_per_citizen)
    assert context.base_statistics['onboardedCitizenCount'] == allowable_citizens
