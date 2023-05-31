from behave import given
from behave import then

from api.idpay import get_initiative_statistics
from conf.configuration import secrets
from conf.configuration import settings
from util.utility import check_statistics


@given('the initiative is "{initiative_name}"')
def step_given_initiative_id(context, initiative_name):
    context.initiatives_settings = settings.initiatives[initiative_name]

    context.initiative_id = secrets.initiatives[initiative_name]['id']
    context.cashback_percentage = context.initiatives_settings['cashback_percentage']
    context.budget_per_citizen = context.initiatives_settings['budget_per_citizen']

    context.base_statistics = get_initiative_statistics(organization_id=secrets.organization_id,
                                                        initiative_id=context.initiative_id).json()
    context.num_new_onboards = 0
    context.num_new_trxs = 0
    context.organization_id = secrets.organization_id


@then('the initiative counters are updated')
def step_check_initiative_statistics_updated(context):
    check_statistics(organization_id=context.organization_id, initiative_id=context.initiative_id,
                     old_statistics=context.base_statistics,
                     onboarded_citizen_count_increment=context.num_onboards,
                     accrued_rewards_increment=context.expected_accrued,
                     rewarded_trxs_increment=context.num_trx)
