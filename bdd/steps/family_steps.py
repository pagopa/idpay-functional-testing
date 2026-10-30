from behave import given

from api.mock import get_family_from_user_id
from api.mock import put_mocked_family
from util.data_vault_utilities import tokenize_fc


@given('citizens {citizens_names} are in the same family')
def step_given_same_family_id(context, citizens_names):
    citizens = citizens_names.split()

    user_ids = [
        tokenize_fc(fiscal_code= context.citizens_fc[name])
        for name in citizens
    ]
    citizens_fc = [
        context.citizens_fc[name]
        for name in citizens
    ]
    res = put_mocked_family(citizens_cf = citizens_fc)
    assert res.status_code == 200

    family_id = res.json()["familyId"]

    res = get_family_from_user_id(user_id=user_ids[0])
    assert res.status_code == 200

    assert res.json()["familyId"] == family_id
    assert set(res.json()["memberIds"]) == set(user_ids)
