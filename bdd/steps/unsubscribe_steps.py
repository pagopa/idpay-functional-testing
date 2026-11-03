from behave import given
from behave import when

from util.utility import citizen_unsubscribe_from_initiative


@given('the citizen {citizen_name} unsubscribes')
@when('the citizen {citizen_name} unsubscribes')
def step_citizen_unsubscribes(context, citizen_name):
    citizen_unsubscribe_from_initiative(initiative_id=context.initiative_id,
                                        fiscal_code=context.citizens_fc[citizen_name])
