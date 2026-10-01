"""Product setup and observable status/audit assertions."""
import uuid

from behave import given
from behave import then
from behave import when

from util import rdb_utilities as rdb


@given('RDB product "{name}" has initial status "{status}"')
def rdb_initial_product(context, name, status):
    rdb.seed_product(context, name, status)


@given('RDB product "{name}" does not exist')
def rdb_missing_product(context, name):
    s = rdb.state(context)
    s.products[name] = {'gtinCode': uuid.uuid4().hex[:14], 'initiativeId': s.initiative_id,
                        'organizationId': s.organization_id}
    assert not rdb.products(context, gtin_code=s.products[name]['gtinCode'])


@when('the RDB user changes products "{names}" from "{current}" to "{target}"')
def rdb_update_status(context, names, current, target):
    s = rdb.state(context)
    s.current_status, s.target_status = current, target
    s.response = rdb.change_status(context, [name.strip() for name in names.split(',')], current, target)


@then('RDB product "{name}" has status "{status}"')
def rdb_product_status(context, name, status):
    assert rdb.get_product(context, name)['status'] == status


@then('RDB product "{name}" is unchanged')
def rdb_product_unchanged(context, name):
    assert rdb.get_product(context, name) == rdb.state(context).before[name]


@then('RDB product "{name}" remains absent')
def rdb_product_absent(context, name):
    assert not rdb.products(context, gtin_code=rdb.state(context).products[name]['gtinCode'])


@then('RDB product "{name}" records the requested status change')
def rdb_status_audit(context, name):
    s = rdb.state(context)
    product = rdb.get_product(context, name)
    previous = s.before[name].get('statusChangeChronology', [])
    chronology = product['statusChangeChronology']
    assert len(chronology) == len(previous) + 1
    added = [event for event in chronology if event not in previous]
    assert len(added) == 1
    event = added[0]
    assert event['currentStatus'] == s.current_status
    assert event['targetStatus'] == s.target_status
    assert event['role'] == ('L1' if s.role == 'invitalia' else 'L2')
    assert event['username'] == s.username
    assert event['updateDate']
    assert event['motivation'] == 'RDB functional test'
    if s.target_status == 'REJECTED':
        assert product['formalMotivation'] == 'RDB functional test'
