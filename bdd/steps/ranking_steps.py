import json
from math import floor

import pandas as pd
from behave import then
from behave import when

from api.idpay import force_ranking
from api.idpay import get_ranking_file
from api.idpay import put_publish_ranking
from api.idpay import put_ranking_end_date
from conf.configuration import secrets
from util.encrypt_utilities import verify_and_clear_p7m_file
from util.utility import get_selfcare_token


@when('the ranking period ends and the institution publishes the ranking')
def step_end_ranking(context):
    institution_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    res = put_ranking_end_date(initiative_id=context.initiative_id)
    assert res.status_code == 200

    res = force_ranking()
    assert res.status_code == 200

    ranking_file_path = None

    for i in res.json():
        if i['initiativeId'] == context.initiative_id and i['rankingStatus'] == 'READY':
            ranking_file_path = i['rankingFilePath']
            break

    assert ranking_file_path is not None

    res = put_publish_ranking(selfcare_token=institution_token, initiative_id=context.initiative_id)
    assert res.status_code == 204

    res = get_ranking_file(selfcare_token=institution_token, initiative_id=context.initiative_id,
                           ranking_file_path=ranking_file_path.split('/')[-1])
    assert res.status_code == 200
    response_content_filename = '-'.join(ranking_file_path.split('/')[1:3])
    clear_ranking_filename = response_content_filename + '.clear.csv'

    with open(response_content_filename, 'wb') as f:
        f.write(res.content)

    verify_and_clear_p7m_file(input_file_name=response_content_filename, output_file_name=clear_ranking_filename)

    with open(clear_ranking_filename, 'r') as input_file:
        ranking = pd.read_csv(input_file, quotechar='"', sep=';')
        context.ranking = list(ranking.values)


@then('{rank_order} are ranked in the correct order')
def step_check_ranking_order(context, rank_order):
    rank_order = json.loads(rank_order)
    rank_order_fc = (context.citizens_fc[name] for name in rank_order)
    print('---')
    for count, citizen in enumerate(rank_order_fc):
        curr_rank = context.ranking[count]
        assert curr_rank[4] == 'ELIGIBLE_OK'
        assert curr_rank[3] == count + 1
        assert citizen == curr_rank[0]
        assert context.citizen_isee[citizen] == floor(curr_rank[2]) / 100
