import json

from behave import given

from api.mock import get_family_from_id
from api.mock import put_mocked_family
from api.pdv import detokenize_pdv_token


@given('citizens <citizens> are in the same family')
def step_given_same_family_id(context, citizens):
    citizens = json.loads(citizens)
    citizens = (context.citizens_fc[name] for name in citizens)
    res = put_mocked_family(family=list(citizens))
    assert res.status_code == 200
    context.family_id = res.json()['familyId']

    res = get_family_from_id(family_id=context.family_id)
    assert res == 200
    assert res.json()['familyId'] == context.family_id
    assert set(detokenize_pdv_token(x) for x in res.json()['memberIds']) == set(citizens)
