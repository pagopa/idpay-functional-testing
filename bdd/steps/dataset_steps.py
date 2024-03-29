import datetime
import random
import uuid

import pytz
from behave import given

from api.mock import control_mocked_isee
from conf.configuration import settings
from util.dataset_utility import fake_fc
from util.utility import get_io_token


@given('the citizen {citizen_name} has fiscal code {citizen_fc}')
def step_citizen_fc_exact_or_random(context, citizen_name, citizen_fc):
    if citizen_fc == 'random':
        citizen_fc = fake_fc()

    context.latest_citizen_fc = citizen_fc
    context.latest_token_io = get_io_token(citizen_fc)

    try:
        context.citizens_fc[citizen_name] = citizen_fc
    except AttributeError:
        context.citizens_fc = {citizen_name: citizen_fc}


@given('citizens {citizens_names} have fiscal code random')
def step_citizens_fc_exact_or_random(context, citizens_names: str):
    citizens = citizens_names.split()
    for c in citizens:
        step_citizen_fc_exact_or_random(context=context, citizen_name=c, citizen_fc='random')


@given('the citizen {citizen_name} is {age} years old {precision}')
def step_citizen_fc_from_name_age_and_precision(context, citizen_name: str, age: int, precision: str):
    citizen_fc = fake_fc(age=age)
    if precision == 'at most':
        current_date = datetime.datetime.now() - datetime.timedelta(
            days=random.randint(1, datetime.datetime.now().day))
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

    context.latest_citizen_fc = citizen_fc
    context.latest_token_io = get_io_token(citizen_fc)

    try:
        context.citizens_fc[citizen_name] = citizen_fc
    except AttributeError:
        context.citizens_fc = {citizen_name: citizen_fc}


@given('the citizen {citizen_name} has ISEE {isee} of type "{isee_type}"')
def step_set_citizen_isee(context, citizen_name: str, isee: int, isee_type: str):
    isee = float(isee)
    res = control_mocked_isee(fc=context.citizens_fc[citizen_name], isee=isee, isee_type=isee_type)
    assert res.status_code == 200

    context.citizen_isee[context.citizens_fc[citizen_name]] = isee


@given('citizens {citizens_names} have ISEE {isee} of type "{isee_type}"')
def step_set_citizens_isee(context, citizens_names: str, isee: int, isee_type: str):
    citizens = citizens_names.split()
    for c in citizens:
        step_set_citizen_isee(context=context, citizen_name=c, isee=isee, isee_type=isee_type)


@given('citizens {citizens_names} are selected for the initiative with whitelist')
def step_citizens_in_whitelist(context, citizens_names: str):
    citizens_names = citizens_names.split()
    known_beneficiaries = []
    for citizen_name in citizens_names:
        citizen_fc = context.citizens_fc[citizen_name]
        known_beneficiaries.append(citizen_fc)

    if 'known_beneficiaries' not in context:
        context.known_beneficiaries = []

    context.known_beneficiaries = known_beneficiaries


@given('the transaction {trx_name} does not exists')
def step_trx_does_not_exists(context, trx_name):
    context.transactions[trx_name] = {'trxCode': str(uuid.uuid4())[:8],
                                      'id': str(uuid.uuid4())}


@given('the transaction is created before fruition period')
def step_trx_before_fruition_period(context):
    context.trx_date = (
            datetime.datetime.strptime(context.fruition_start, settings.iso_date_format) - datetime.timedelta(
        days=1)).strftime(
        settings.iso_date_format)


@given('the transaction is created {days_back} days ago')
def step_trx_date_days_ago(context, days_back):
    context.trx_date = (
            datetime.datetime.now(pytz.timezone('Europe/Rome')) - datetime.timedelta(days=int(days_back))).strftime(
        settings.iso_date_format)
