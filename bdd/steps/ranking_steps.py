import json
from math import floor

import pandas as pd
from behave import given
from behave import then
from behave import when

from api.idpay import force_ranking
from api.idpay import get_ranking_file
from api.idpay import put_publish_ranking
from api.idpay import put_ranking_end_date
from bdd.steps.onboarding_steps import step_check_onboarding_status
from conf.configuration import secrets
from util.encrypt_utilities import verify_and_clear_p7m_file
from util.utility import check_ranking_status_institution_portal
from util.utility import get_selfcare_token


@given('the ranking period ends')
@when('the ranking period ends')
def step_end_ranking(context):
    res = put_ranking_end_date(initiative_id=context.initiative_id)
    assert res.status_code == 200


@given('the ranking is produced')
@when('the ranking is produced')
def step_force_ranking(context):
    res = force_ranking()
    assert res.status_code == 200

    ranking_file_path = None

    for i in res.json():
        if i['initiativeId'] == context.initiative_id and i['rankingStatus'] == 'READY':
            ranking_file_path = i['rankingFilePath']
            break

    assert ranking_file_path is not None

    context.ranking_file_path = ranking_file_path


@given('the institution publishes the ranking')
@when('the institution publishes the ranking')
def step_publish_ranking_(context):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)

    step_force_ranking(context)

    res = put_publish_ranking(selfcare_token=institution_token, initiative_id=context.initiative_id)
    assert res.status_code == 204

    res = get_ranking_file(selfcare_token=institution_token, initiative_id=context.initiative_id,
                           ranking_file_path=context.ranking_file_path.split('/')[-1])
    assert res.status_code == 200
    response_content_filename = '-'.join(context.ranking_file_path.split('/')[1:3])
    clear_ranking_filename = response_content_filename + '.clear.csv'

    with open(response_content_filename, 'wb') as f:
        f.write(res.content)

    verify_and_clear_p7m_file(input_file_name=response_content_filename, output_file_name=clear_ranking_filename)

    try:
        with open(clear_ranking_filename, 'r') as input_file:
            ranking = pd.read_csv(input_file, quotechar='"', sep=';')
            context.ranking = list(ranking.values)
    except pd.errors.EmptyDataError:
        context.ranking = list()


@then('{rank_order} are ranked in the correct order')
def step_check_ranking_order(context, rank_order: str):
    rank_order = json.loads(rank_order)
    rank_order_fc = (context.citizens_fc[name] for name in rank_order)
    for count, citizen in enumerate(rank_order_fc):
        curr_rank = context.ranking[count]
        assert curr_rank[4] == 'ELIGIBLE_OK'
        assert curr_rank[3] == count + 1
        assert citizen == curr_rank[0]
        assert context.citizen_isee[citizen] == floor(curr_rank[2]) / 100
        assert check_ranking_status_institution_portal(initiative_id=context.initiative_id, desired_fc=citizen,
                                                       desired_status='ELIGIBLE_OK'), 'The citizen is either not present or not in the desired status'


@then('the citizen {citizen_name} is not in rank')
def step_check_absence_in_ranking(context, citizen_name: str):
    citizen_fc = context.citizens_fc[citizen_name]
    for rank in context.ranking:
        if citizen_fc == rank[0]:
            assert False, 'The citizen should not be present in ranking'


@then('the citizen {citizen_name} is not eligible')
def step_check_not_eligibility_in_ranking(context, citizen_name: str):
    step_check_onboarding_status(context=context, citizen_name=citizen_name, status='ELIGIBLE_KO')
    citizen_fc = context.citizens_fc[citizen_name]
    for rank in context.ranking:
        if citizen_fc == rank[0]:
            assert rank[4] == 'ELIGIBLE_KO'
    assert check_ranking_status_institution_portal(initiative_id=context.initiative_id, desired_fc=citizen_fc,
                                                   desired_status='ELIGIBLE_KO'), 'The citizen is either not present or not in the desired status'
