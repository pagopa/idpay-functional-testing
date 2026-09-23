"""Fault injection and request observations on explicitly configured WireMock servers."""
import uuid

from api import rdb_test_support as api
from util import rdb_utilities as rdb


def dependency(name):
    return rdb.required(rdb.required(rdb.config(), 'dependencies'), name,
                        'secrets.asset_register.dependencies')


def journal(name):
    response = rdb.success(api.get_requests(rdb.required(dependency(name), 'wiremock_url')))
    return response.json()['requests']


def fail_dependency(context, name):
    fixture = dependency(name)
    assert fixture.get('isolated') is True, 'Fault injection requires an isolated WireMock instance'
    mapping_id = str(uuid.uuid4())
    request = rdb.required(fixture, 'request')
    assert 'urlPath' in request or 'url' in request, 'Configure an exact dependency URL path'
    mapping = {'id': mapping_id, 'priority': 1, 'request': request, 'response': {'status': 503}}
    rdb.success(api.add_mapping(fixture['wiremock_url'], mapping), 201)
    s = rdb.state(context)
    if not hasattr(s, 'faults'):
        s.faults = {}
    s.faults[name] = {'id': mapping_id, 'active': True}
    context.add_cleanup(restore_dependency, context, name)


def restore_dependency(context, name):
    fault = rdb.state(context).faults[name]
    if fault['active']:
        rdb.success(api.delete_mapping(dependency(name)['wiremock_url'], fault['id']))
        fault['active'] = False


def assert_fault_observed(context, name):
    mapping_id = rdb.state(context).faults[name]['id']
    rdb.wait_for(lambda: journal(name),
                 lambda entries: any(entry.get('stubMapping', {}).get('id') == mapping_id
                                     and entry.get('response', {}).get('status') == 503
                                     for entry in entries),
                 f'the backend to encounter the {name} failure')
