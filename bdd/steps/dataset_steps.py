import datetime
import random

from behave import given

from api.token_io import introspect
from util.dataset_utility import fake_fc
from util.utility import get_io_token


@given('the citizen has fiscal code {citizen_fc}')
def step_citizen_fc_exact_or_random(context, citizen_fc):
    if citizen_fc == 'random':
        citizen_fc = fake_fc()

    context.citizen_fc = citizen_fc
    context.token_io = get_io_token(context.citizen_fc)
    res = introspect(context.token_io)
    assert res.json()['fiscal_code'] == context.citizen_fc


@given('the citizen is {age} years old {precision}')
def step_citizen_fc_from_age_and_precision(context, age: int, precision: str):
    citizen_fc = fake_fc(age=age)
    if precision == 'at most':
        current_date = datetime.datetime.now() + datetime.timedelta(days=random.randint(30, 90))
        current_month = current_date.month
        current_day = current_date.day
        citizen_fc = fake_fc(age=age, custom_month=current_month, custom_day=current_day)
    if precision == 'exactly':
        current_date = datetime.datetime.now()
        current_month = current_date.month
        current_day = current_date.day
        citizen_fc = fake_fc(age=age, custom_month=current_month, custom_day=current_day)
    if precision == 'still':
        current_date = datetime.datetime.now()
        current_month = current_date.month
        current_day = current_date.day + 1
        citizen_fc = fake_fc(age=int(age) + 1, custom_month=current_month, custom_day=current_day)
    if precision == 'tomorrow':
        current_date = datetime.datetime.now() + datetime.timedelta(days=1)
        current_month = current_date.month
        current_day = current_date.day
        citizen_fc = fake_fc(age=age, custom_month=current_month, custom_day=current_day)

    context.citizen_fc = citizen_fc
    context.token_io = get_io_token(context.citizen_fc)
    res = introspect(context.token_io)
    assert res.json()['fiscal_code'] == context.citizen_fc


@given('the transaction is created before fruition period')
def step_trx_before_fruition_period(context):
    date_format = '%Y-%m-%dT%H:%M:%S.000%z'
    context.trx_date = (
            datetime.datetime.strptime(context.fruition_start, date_format) - datetime.timedelta(days=1)).strftime(
        date_format)
