"""Authentication, shared assertions and registry queries for RDB."""
import time
from copy import deepcopy

from behave import given  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from behave import then  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from behave import when  # pyright: ignore[reportMissingImports, reportMissingModuleSource]

from api import asset_register as api
from util import rdb_utilities as rdb


@given('the RDB user is authenticated as "{profile}"')
def rdb_authenticate(context, profile):
    rdb.authenticate(context, profile)


@given('the RDB initiative is "{alias}"')
def rdb_initiative(context, alias):
    rdb.select_initiative(context, alias)


@given('the RDB dataset is "{name}"')
def rdb_dataset(context, name):
    rdb.dataset(context, name)


@given('the producer is enabled for the RDB initiative')
def rdb_enabled(context):
    s = rdb.state(context)
    items = rdb.success(api.get_initiatives(s.token)).json()
    assert any(item['initiativeId'] == s.initiative_id and item['enabled'] is True
               for item in items), 'Producer is not enabled for the configured initiative'


@given('the RDB application token fixture is "{name}"')
def rdb_application_token(context, name):
    s = rdb.state(context)
    fixtures = rdb.config().get('application_tokens', {})
    if name == 'expired' and not fixtures.get(name):
        s.token = rdb.expired_application_token(rdb.build_operatore_token_body())
    else:
        s.token = rdb.required(fixtures, name, 'secrets.asset_register.application_tokens')
    if name == 'expired':
        assert rdb.claims(s.token)['exp'] < time.time(), 'The fixture token is not expired'


@given('an RDB application token with "{condition}" is generated')
def rdb_generated_application_token(context, condition):
    rdb.state(context).token = rdb.application_token_for_condition(
        rdb.build_operatore_token_body(), condition)


@then('the generated RDB token identifies the authenticated role and organization')
def rdb_generated_token_claims(context):
    s = rdb.state(context)
    body = rdb.claims(s.token)
    assert body['org_role'] == s.role
    assert body['org_id'] == s.organization_id
    assert body['exp'] > time.time()


@given('the RDB user has no application token')
def rdb_no_token(context):
    rdb.state(context).token = None


@then('the RDB response has HTTP status {status:d}')
def rdb_http_status(context, status):
    rdb.success(rdb.state(context).response, status)


@then('the RDB operation has outcome "{expected}"')
def rdb_outcome(context, expected):
    rdb.outcome(rdb.state(context).response, expected)


@then('the RDB operation fails with error "{error}"')
def rdb_error(context, error):
    body = rdb.outcome(rdb.state(context).response, 'KO')
    assert body.get('errorKey') == error, f'Unexpected error key: {body.get("errorKey")}'


@then('the RDB request is rejected')
def rdb_rejected(context):
    rdb.rejected(rdb.state(context).response)


@when('the RDB user requests the initiatives')
def rdb_get_initiatives(context):
    s = rdb.state(context)
    s.response = api.get_initiatives(s.token)


@then('the returned RDB initiative IDs match the dataset')
def rdb_initiative_ids(context):
    s = rdb.state(context)
    actual = [item['initiativeId'] for item in rdb.success(s.response).json()]
    assert sorted(actual) == sorted(rdb.required(s.dataset, 'initiative_ids'))


@then('the RDB initiatives are enabled')
def rdb_initiatives_enabled(context):
    assert all(item['enabled'] is True for item in rdb.success(rdb.state(context).response).json())


@then('the RDB initiatives are ordered by name')
def rdb_initiatives_ordered(context):
    names = [item['initiativeName'] for item in rdb.success(rdb.state(context).response).json()]
    assert len(names) >= 2, 'Sorting fixture must contain at least two initiatives'
    assert names == sorted(names)


@when('the RDB user requests the dataset products')
def rdb_dataset_products(context):
    s = rdb.state(context)
    s.items = rdb.products(context, organization_id=rdb.required(s.dataset, 'organization_id'))


@then('the returned RDB product GTINs match the dataset')
def rdb_product_ids(context):
    s = rdb.state(context)
    assert sorted(item['gtinCode'] for item in s.items) == sorted(rdb.required(s.dataset, 'product_gtins'))


@then('the returned RDB products belong to the expected organization and initiative')
def rdb_product_scope(context):
    s = rdb.state(context)
    assert s.items, 'Scope fixture must include visible products'
    assert all(item['initiativeId'] == s.initiative_id and
               item['organizationId'] == s.dataset['organization_id'] for item in s.items)


@when('the RDB user filters products by "{fields}"')
def rdb_product_filters(context, fields):
    s = rdb.state(context)
    fixture = rdb.required(s.dataset, 'filters')
    s.filters = deepcopy(s.dataset.get('query_scope', {}))
    s.filter_names = [field.strip() for field in fields.split(',')]
    for field in s.filter_names:
        argument, _ = rdb.FILTER_FIELDS[field]
        s.filters[argument] = rdb.required(fixture, field)
    s.items = rdb.products(context, **s.filters)


@given('RDB products are prepared for filter "{fields}"')
def rdb_prepare_product_filter(context, fields):
    rdb.prepare_product_filter(context, fields)


@then('only RDB products matching the selected filters are returned')
def rdb_matches_filters(context):
    s = rdb.state(context)
    key = ', '.join(s.filter_names)
    expected = rdb.required(rdb.required(s.dataset, 'filter_product_gtins'), key)
    assert expected, 'Use nonempty filter fixtures to avoid vacuous assertions'
    assert sorted(item['gtinCode'] for item in s.items) == sorted(expected)
    # Expected GTINs are necessary for productFileId (not exposed by ProductDTO)
    # and for API filters that use partial, case-insensitive matching.


@when('the RDB user searches for product "{name}"')
def rdb_search_product(context, name):
    s = rdb.state(context)
    s.items = rdb.products(context, gtin_code=s.products[name]['gtinCode'])


@then('the RDB product list is empty')
def rdb_empty_products(context):
    assert rdb.state(context).items == []


@when('the RDB user requests the CSV batches')
def rdb_batches(context):
    s = rdb.state(context)
    s.response = api.get_product_files_batch_list(
        s.token, s.initiative_id, rdb.required(s.dataset, 'organization_id'))


@then('the returned RDB batch IDs match the dataset')
def rdb_batch_ids(context):
    s = rdb.state(context)
    actual = [item['productFileId'] for item in rdb.success(s.response).json()]
    assert sorted(actual) == sorted(rdb.required(s.dataset, 'batch_ids'))


@when('the RDB user requests the producers')
def rdb_producers(context):
    s = rdb.state(context)
    s.items = rdb.collect_pages(lambda page: api.get_producers(s.token, s.initiative_id, page=page))


@then('the returned RDB producer IDs match the dataset')
def rdb_producer_ids(context):
    s = rdb.state(context)
    assert sorted(item['producerId'] for item in s.items) == sorted(rdb.required(s.dataset, 'producer_ids'))


@then('the RDB producer list is consistent with known initiative memberships')
def rdb_known_producer_ids(context):
    s = rdb.state(context)
    if 'producer_ids' in s.dataset:
        rdb_producer_ids(context)
        return
    ids = [item['producerId'] for item in s.items]
    known = set(rdb.required(s.dataset, 'known_producer_ids'))
    assert known, 'Producer list verification requires known memberships'
    assert len(ids) == len(set(ids)), 'Producer list contains duplicate associations'
    assert all(item.get('producerId') and item.get('producerName') for item in s.items), (
        'Producer list contains incomplete identities')
    assert known <= set(ids), 'Producer list omits known initiative memberships'
    assert set(s.dataset.get('foreign_producer_ids', [])).isdisjoint(ids), (
        'Producer list includes an association belonging only to another initiative')


@when('the RDB user requests the producer details')
def rdb_producer_details(context):
    s = rdb.state(context)
    s.response = api.get_institution_by_id(s.token, rdb.required(s.dataset, 'institution_id'))


@then('the RDB producer details identify the requested institution')
def rdb_institution_details(context):
    s = rdb.state(context)
    rdb.assert_institution_details(rdb.success(s.response).json(),
                                  rdb.required(s.dataset, 'institution_expected', 'dataset'))
