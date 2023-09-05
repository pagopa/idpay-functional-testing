from behave import given

from util.utility import citizen_unsubscribe_from_initiative


@given('the citizen {citizen_name} is unsubscribed')
def step_institution_suspends_citizen(context, citizen_name):
    citizen_unsubscribe_from_initiative(initiative_id=context.initiative_id,
                                        fiscal_code=context.citizens_fc[citizen_name])
