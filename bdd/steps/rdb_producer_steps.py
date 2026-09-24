"""Producer imports and operational email persistence checks."""
from behave import given
from behave import then
from behave import when

from api import asset_register as api
from util import rdb_utilities as rdb


def association(context):
    s = rdb.state(context)
    return {
        'initiativeId': s.initiative_id,
        'producerId': s.organization_id,
        'producerName': s.bodies[s.profile]['orgName'],
        'producerEmail': 'rdb@example.it',
    }


def initiative_details(context):
    s = rdb.state(context)
    items = rdb.success(api.get_initiatives(s.token)).json()
    matching = [item for item in items if item['initiativeId'] == s.initiative_id]
    assert len(matching) == 1, 'Expected exactly one producer initiative association'
    return matching[0]


@given('the RDB producer association payload is "{condition}"')
def rdb_association_payload(context, condition):
    s = rdb.state(context)
    s.associations = [association(context)]
    if condition == 'empty':
        s.associations = []
    elif condition.startswith('missing '):
        del s.associations[0][condition.removeprefix('missing ')]
    else:
        assert condition == 'valid', f'Unknown association case: {condition}'


@given('the RDB producer association payload has email "{email}"')
def rdb_association_email(context, email):
    rdb_association_payload(context, 'valid')
    rdb.state(context).associations[0]['producerEmail'] = email


@when('the RDB producer associations are imported')
def rdb_import(context):
    s = rdb.state(context)
    s.response = api.import_producers(s.associations)


@given('the RDB producer association has already been imported')
def rdb_previous_import(context):
    rdb_import(context)
    rdb_import_counts(context, 1, 1, 0)
    rdb_association_stored(context)


@then('the RDB import counts are {received:d} received, {imported:d} imported and {failed:d} failed')
def rdb_import_counts(context, received, imported, failed):
    body = rdb.success(rdb.state(context).response).json()
    assert body['totalRecords'] == received
    assert body['importedRecords'] == imported
    assert body['failedRecords'] == failed
    assert received == imported + failed
    assert body['status'] == ('PARTIAL' if failed else 'OK')


@then('the RDB producer association is stored once')
def rdb_association_stored(context):
    s = rdb.state(context)
    producer_token = s.token
    operator_token = rdb.authenticate(context, 'Invitalia')
    items = rdb.collect_pages(lambda page: api.get_producers(operator_token, s.initiative_id, page=page))
    producer_id = s.associations[0]['producerId']
    matches = [item for item in items if item['producerId'] == producer_id]
    assert len(matches) == 1
    assert matches[0]['producerName'] == s.associations[0]['producerName']
    rdb.authenticate(context, 'producer')
    assert s.token == producer_token
    assert initiative_details(context)['enabled'] is True


@given('the RDB operational email was set to "{email}"')
def rdb_initial_email(context, email):
    rdb_set_email(context, email)
    rdb.outcome(rdb.state(context).response)
    rdb_email_stored(context, email)


@when('the producer sets the RDB operational email to "{email}"')
def rdb_set_email(context, email):
    s = rdb.state(context)
    s.response = api.update_operative_email(s.token, s.organization_id, s.initiative_id, email)


@then('the RDB operational email is "{email}"')
def rdb_email_stored(context, email):
    expected = None if email == 'null' else email
    assert initiative_details(context).get('organizationEmail') == expected


@given('the RDB operational email is initially absent')
def rdb_email_absent(context):
    assert initiative_details(context).get('organizationEmail') is None
