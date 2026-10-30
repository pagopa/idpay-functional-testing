import datetime

import pytz
from behave import given

from api.idpay import post_initiative_info
from conf.configuration import secrets
from conf.configuration import settings
from util.utility import create_initiative
from util.utility import create_initiative_and_update_conf
from util.utility import get_selfcare_token
from util.utility import retry_institution_statistics


@given("the initiative is active")
def step_given_active_initiative(context):
    initiative_name = context.initiative_config["initiative_id"]
    print(f"Initiative selected: {initiative_name}")
    context.feature_initiative_names.add(initiative_name)
    if initiative_name not in secrets["initiatives"]:
        secrets["initiatives"][initiative_name] = {}
        create_initiative_and_update_conf(initiative_name=initiative_name)
    context.initiative_name = initiative_name
    context.initiative_id = secrets["initiatives"][initiative_name]["id"]
    context.organization_id = secrets["initiatives"][initiative_name]["organization_id"]
    context.initiative_settings = settings.initiatives[initiative_name]
    context.organization_id = secrets.initiatives[initiative_name]['organization_id']
    base_context_initialization(context)


def base_context_initialization(context):
    context.cashback_percentage = context.initiative_settings.get('cashback_percentage')
    context.budget_per_citizen = context.initiative_settings['budget_per_citizen']
    context.fruition_start = context.initiative_settings['fruition_start']
    context.total_budget = context.initiative_settings.get('total_budget')

    context.trx_date = (datetime.datetime.now(pytz.timezone('Europe/Rome')) + datetime.timedelta(days=1)).strftime(
        settings.iso_date_format)

    if not hasattr(context, 'organization_id'):
        context.organization_id = secrets.organization_id

    context.base_statistics = retry_institution_statistics(initiative_id=context.initiative_id,
                                                           organization_id=context.organization_id)
    context.base_merchants_statistics = {}

    context.transactions = {}

    context.num_new_onboards = 0

    if 'citizens_fc' not in context:
        context.citizens_fc = {}

    context.num_new_trxs = 0

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


@given('the new initiative {initiative_name} is created')
def step_new_initiative_created(context, initiative_name):
    initiative_id = create_initiative(initiative_name)
    if (secrets.initiatives.get(initiative_name) is None):
        secrets.initiatives[initiative_name] = {'id': None}
    secrets.initiatives[initiative_name]['id'] = initiative_id
    secrets["newly_created"].add(initiative_id)


@given('the new initiative {initiative_name} is created but not published')
def step_new_initiative_created_but_not_published(context, initiative_name):
    token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)

    response = post_initiative_info(token, initiative_name)
    assert response.status_code == 201, "Unexpected status code when creating initiative: {}".format(response.status_code)
    if (secrets.initiatives.get(initiative_name) is None):
        secrets.initiatives[initiative_name] = {'id': None, 'organization_id': secrets.selfcare_info.test_institution.orgId}
    secrets.initiatives[initiative_name]['id'] = response.json().get('initiativeId')
    assert secrets.initiatives[initiative_name]['id'] is not None, "Failed to retrieve initiative ID from response"
    secrets["newly_created"].add(secrets.initiatives[initiative_name]["id"]) 


@given('the initiative is "{initiative_name}"')
def step_given_initiative_name(context, initiative_name):
    context.initiative_name = initiative_name
    context.initiative_id = secrets["initiatives"][initiative_name]["id"]
    context.initiative_settings = settings.initiatives[initiative_name]
    context.organization_id = secrets["initiatives"][initiative_name]["organization_id"]
    base_context_initialization(context)
