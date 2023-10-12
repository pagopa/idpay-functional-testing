import json

from behave import given

from api.mock import get_family_from_user_id
from api.mock import put_mocked_family
from util.utility import detokenize_to_fc
from util.utility import tokenize_fc


@given('citizens {citizens} are in the same family')
def step_given_same_family_id(context, citizens: str):
    citizens = json.loads(citizens)
    citizens_fc = list((context.citizens_fc[name] for name in citizens))
    res = put_mocked_family(family=json.dumps(citizens_fc))
    assert res.status_code == 200
    family_id = res.json()['familyId']

    res = get_family_from_user_id(user_id=tokenize_fc(citizens_fc[0]))
    assert res.status_code == 200
    assert res.json()['familyId'] == family_id
    assert set(detokenize_to_fc(x) for x in res.json()['memberIds']) == set(citizens_fc)
