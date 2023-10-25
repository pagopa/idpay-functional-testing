import json

from behave import given
from behave import then

from api.idpay import wallet
from api.mock import get_family_from_user_id
from api.mock import put_mocked_family
from util.utility import detokenize_to_fc
from util.utility import get_io_token
from util.utility import retry_wallet
from util.utility import tokenize_fc


@given('citizens {citizens_names} are in the same family')
def step_given_same_family_id(context, citizens_names: str):
    citizens = citizens_names.split()
    citizens_fc = list((context.citizens_fc[name] for name in citizens))
    res = put_mocked_family(family=json.dumps(citizens_fc))
    assert res.status_code == 200
    family_id = res.json()['familyId']

    res = get_family_from_user_id(user_id=tokenize_fc(citizens_fc[0]))
    assert res.status_code == 200
    assert res.json()['familyId'] == family_id
    assert set(detokenize_to_fc(x) for x in res.json()['memberIds']) == set(citizens_fc)


@then('the family member {citizen_name} has budget of {amount_left} euros left')
def step_check_family_member_budget_left(context, citizen_name, amount_left):
    expected_amount_left = float(amount_left)
    curr_token_io = get_io_token(context.citizens_fc[citizen_name])

    retry_wallet(expected=expected_amount_left, request=wallet, token=curr_token_io,
                 initiative_id=context.initiative_id, field='amount', tries=10, delay=2)


@then('the family members {citizens_names} have budget of {amount_left} euros left')
def step_check_family_members_budget_left(context, citizens_names, amount_left):
    citizens = citizens_names.split()
    for citizen in citizens:
        step_check_family_member_budget_left(context=context, citizen_name=citizen, amount_left=amount_left)


@then('the family member {citizen_name} is rewarded with {expected_accrued} euros')
def step_check_rewards_of_citizen(context, citizen_name, expected_accrued):
    expected_accrued = float(expected_accrued)
    curr_token_io = get_io_token(context.citizens_fc[citizen_name])

    retry_wallet(expected=expected_accrued, request=wallet, token=curr_token_io,
                 initiative_id=context.initiative_id, field='accrued', tries=10, delay=2)
