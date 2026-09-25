"""Scenario-scoped RDB fixtures, CSV generation and bounded API polling."""
import base64
import json
import time
import uuid
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit

from api import asset_register as api
from conf.configuration import secrets
from util.asset_register_utilities import build_l1_token_body
from util.asset_register_utilities import build_l2_token_body
from util.asset_register_utilities import build_operatore_token_body
from util.asset_register_utilities import fake_product_file
from util.rdb_csv_data import cooking_products
from util.rdb_csv_data import csv_bytes
from util.rdb_csv_data import HEADERS

PROFILE_BUILDERS = {
    'producer': build_operatore_token_body,
    'Invitalia': build_l1_token_body,
    'Invitalia Admin': build_l2_token_body,
}
FILTER_FIELDS = {
    'category': ('category', 'category'),
    'CSV upload': ('product_file_id', 'productFileId'),
    'EPREL code': ('eprel_code', 'eprelCode'),
    'GTIN': ('gtin_code', 'gtinCode'),
    'product name': ('product_name', 'productName'),
    'brand': ('brand', 'brand'),
    'model': ('model', 'model'),
    'status': ('status', 'status'),
}


def required(mapping, key, location='secrets.asset_register'):
    value = mapping.get(key)
    assert value is not None, f'Missing {location}.{key}; see docs/rdb.md'
    return value


def config():
    return required(secrets, 'asset_register', 'secrets')


def state(context):
    if not hasattr(context, 'rdb'):
        context.rdb = SimpleNamespace(
            tokens={}, bodies={}, products={}, before={}, dataset={}, filters={},
            category='COOKINGHOBS', response=None, csv_file=None,
            initiative_id=None, role=None, token=None, upload=None,
            current_status=None, target_status=None, report=None,
        )
    return context.rdb


def success(response, status=200):
    if response.status_code != status:
        endpoint = f' ({response.request.method} {urlsplit(response.url).path})' if response.url and response.request else ''
        raise AssertionError(f'Expected HTTP {status}, got {response.status_code}{endpoint}')
    return response


def outcome(response, expected='OK'):
    body = success(response).json()
    assert body.get('status') == expected, (
        f'Expected {expected}, got status={body.get("status")}, errorKey={body.get("errorKey")}'
    )
    return body


def rejected(response):
    # Routing errors and server failures must not pass as business rejections.
    assert response is not None, 'No RDB request has been executed'
    if response.status_code not in (400, 401, 403, 409, 422):
        outcome(response, 'KO')


def token_from_response(response):
    token = success(response).text.strip().strip('"')
    assert len(token.split('.')) == 3, 'RDB did not return a JWT'
    return token


def claims(token):
    """Decode for assertions only; this does not verify a JWT signature."""
    payload = token.split('.')[1]
    return json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))


def assert_institution_details(body, expected):
    """APIM returns InstitutionResponse without an id; compare independent identity data."""
    assert str(body.get('description') or '').strip(), 'Institution description is missing'
    fields = ('vatNumber', 'description') if 'description' in expected else ('vatNumber',)
    for field in fields:
        assert expected.get(field) and expected[field] != '-', f'Missing expected institution {field}'
        assert body.get(field) == expected[field], f'Institution {field} does not match the fixture'


def get_rdb_access_token(body):
    """Issue an application JWT through /idpay-itn/register/token/test.

    Like get_merchant_access_token, use the API's test signer and check issuance.
    Keep the supplied profile unchanged; never print the response JWT.
    """
    return token_from_response(api.post_token_test(deepcopy(body)))


def expired_application_token(body):
    """Ask the test signer for an expired JWT; never edit an already signed token."""
    payload = deepcopy(body)
    payload['exp'] = int(time.time()) - 3600
    token = get_rdb_access_token(payload)
    decoded = claims(token)
    assert decoded['exp'] == payload['exp'], (
        'Test signer did not preserve the requested expiration; deploy the exp override '
        'from jwt_register_token_test.xml.tpl or configure application_tokens.expired'
    )
    for field in ('iss', 'aud'):
        assert decoded[field] == payload[field], f'Test signer did not preserve {field}'
    return token


def application_token_for_condition(body, condition):
    """Keep issuer/audience cases server-signed; corrupt only the signature case."""
    payload = deepcopy(body)
    overrides = {'invalid issuer': ('iss', 'https://invalid.example.test'),
                 'invalid audience': ('aud', 'invalid.rdb.audience')}
    assert condition in (*overrides, 'invalid signature'), 'Unsupported token condition'
    if condition in overrides:
        field, value = overrides[condition]
        payload[field] = value
    token = get_rdb_access_token(payload)
    decoded = claims(token)
    assert decoded['exp'] > time.time(), 'Generated application token is expired'
    for field in ('iss', 'aud'):
        assert decoded[field] == payload[field], f'Test signer did not preserve {field}'
    if condition == 'invalid signature':
        header, content, signature = token.split('.')
        signature_bytes = bytearray(base64.urlsafe_b64decode(signature + '=' * (-len(signature) % 4)))
        signature_bytes[0] ^= 1
        signature = base64.urlsafe_b64encode(signature_bytes).decode().rstrip('=')
        token = f'{header}.{content}.{signature}'
    return token


def register_profile(context, profile, body):
    """Store a scenario-owned profile only after token issuance succeeds."""
    s = state(context)
    body = deepcopy(body)
    token = get_rdb_access_token(body)
    s.bodies[profile] = body
    s.tokens[profile] = token


def authenticate(context, profile):
    s = state(context)
    if profile not in s.tokens:
        if profile in PROFILE_BUILDERS:
            body = PROFILE_BUILDERS[profile]()
        else:
            body = required(required(config(), 'profiles'), profile,
                            'secrets.asset_register.profiles')
        register_profile(context, profile, body)
    s.profile = profile
    s.token = s.tokens[profile]
    s.role = s.bodies[profile]['orgRole']
    s.organization_id = s.bodies[profile]['orgId']
    s.username = f'{s.bodies[profile]["familyName"]} {s.bodies[profile]["name"]}'
    return s.token


def select_initiative(context, alias):
    s = state(context)
    configured_id = config().get('initiatives', {}).get(alias)
    if configured_id:
        s.initiative_id = configured_id
    else:
        initiative_name = {'A': 'bonus_elettrodomestici', 'B': 'bonus_decoder'}.get(alias, alias)
        initiative = required(secrets.get('initiatives', {}), initiative_name, 'secrets.initiatives')
        s.initiative_id = required(initiative, 'id', f'secrets.initiatives.{initiative_name}')
        assert s.initiative_id, f'Empty secrets.initiatives.{initiative_name}.id'
    return s.initiative_id


def dataset(context, name):
    from util.rdb_dataset_builders import BUILDERS
    s = state(context)
    configured = config().get('datasets', {})
    builders = {
        **BUILDERS,
        'producer without initiatives': producer_without_initiatives,
        'upload without report': upload_without_report,
    }
    if name in configured:
        s.dataset = deepcopy(configured[name])
    elif name in builders:
        s.dataset = builders[name](context)
    else:
        s.dataset = deepcopy(required(configured, name, 'secrets.asset_register.datasets'))
    if 'profile' in s.dataset:
        authenticate(context, s.dataset['profile'])
    if 'initiative' in s.dataset:
        select_initiative(context, s.dataset['initiative'])
    assert s.token is not None, f'Dataset {name} must select an authenticated profile'
    return s.dataset


def producer_without_initiatives(context):
    """Issue a test token for a fresh organization with no imported association."""
    body = build_operatore_token_body()
    body.update(orgId=str(uuid.uuid4()), uid=str(uuid.uuid4()), orgName='RDB unassociated producer')
    profile = 'generated producer without initiatives'
    register_profile(context, profile, body)
    authenticate(context, profile)
    return {'initiative_ids': []}


def upload_generated_csv(context, rows=None):
    """Create an upload and locate its terminal history record by its unique filename."""
    set_csv(context, rows)
    return finish_upload(context)


def finish_upload(context):
    """Submit the prepared fixture and require all its rows to be loaded."""
    outcome(submit_csv(context))
    upload = completed_upload(context)
    assert upload['uploadStatus'] == 'LOADED', 'Dataset CSV was not completely loaded'
    return upload


def upload_without_report(context):
    authenticate(context, 'producer')
    upload = upload_generated_csv(context)
    return {'product_file_id': upload['productFileId']}


def prepare_csv_history(context, count):
    assert count > 0
    authenticate(context, 'producer')
    for _ in range(count):
        upload_generated_csv(context)


def prepare_product_filter(context, field):
    """Generate positive/control rows for filters that can use unique CSV values."""
    generated_fields = {'CSV upload', 'GTIN', 'product name', 'brand', 'model'}
    if 'product filters' in config().get('datasets', {}) or field not in generated_fields:
        dataset(context, 'product filters')
        return
    authenticate(context, 'producer')
    rows = cooking_products(3)
    marker = uuid.uuid4().hex
    for row in rows[:2]:
        row[4], row[5] = f'RDB {marker}', f'Model {marker}'
    rows[2][4], rows[2][5] = f'Control {uuid.uuid4().hex}', f'Other {uuid.uuid4().hex}'
    target = rows[:2]
    if field == 'CSV upload':
        upload = upload_generated_csv(context, target)
        upload_generated_csv(context, rows[2:])
    else:
        upload = upload_generated_csv(context, rows)
    values = {
        'CSV upload': upload['productFileId'],
        'GTIN': target[0][0],
        'product name': marker,
        'brand': target[0][4],
        'model': target[0][5],
    }
    expected = [row[0] for row in (target[:1] if field == 'GTIN' else target)]
    state(context).dataset = {
        'filters': {field: values[field]},
        'filter_product_gtins': {field: expected},
    }


def set_csv(context, rows=None, headers=None, category='COOKINGHOBS'):
    s = state(context)
    s.rows = cooking_products() if rows is None else rows
    s.headers = HEADERS[:] if headers is None else headers
    s.category = category
    s.csv_file = (f'rdb-{uuid.uuid4().hex}.csv', csv_bytes(s.headers, s.rows), 'text/csv')
    return s.csv_file


def eprel_csv(context, case):
    defaults = json.loads((Path(__file__).resolve().parents[1] /
                           'conf/rdb/eprel.json').read_text(encoding='utf-8'))
    fixture = required({**defaults, **config().get('eprel', {})}, case, 'secrets.asset_register.eprel')
    headers = fake_product_file(0)[1].decode('utf-8').split(';')
    rows = deepcopy(required(fixture, 'rows', f'asset_register.eprel.{case}'))
    gtin_index = headers.index('Codice GTIN/EAN')
    for row in rows:
        row[gtin_index] = uuid.uuid4().hex[:14]
    set_csv(context, rows, headers, required(fixture, 'category'))
    state(context).eprel_fixture = fixture


def collect_pages(fetch):
    page, items = 0, []
    while True:
        body = success(fetch(page)).json()
        assert isinstance(body.get('content'), list), 'Missing page content'
        assert body['pageNo'] == page, 'Server returned the wrong page'
        items.extend(body['content'])
        page += 1
        if page >= body['totalPages']:
            assert len(items) == body['totalElements'], 'Pagination changed or lost records'
            return items
        assert page < 10000, 'Pagination did not terminate'


def history(context):
    s = state(context)
    return collect_pages(lambda page: api.get_product_files(s.token, s.initiative_id, page=page, size=100))


def products(context, **filters):
    s = state(context)
    if s.role == 'operatore':
        filters.setdefault('organization_id', s.organization_id)
    return collect_pages(lambda page: api.get_products(
        s.token, s.initiative_id, role=s.role, page=page, size=100, **filters))


def wait_for(fetch, predicate, description, poll_interval=None):
    timeout = float(config().get('poll_timeout', 120))
    interval = float(config().get('poll_interval', 2) if poll_interval is None else poll_interval)
    assert timeout > 0 and interval > 0, 'Polling settings must be positive'
    deadline = time.monotonic() + timeout
    while True:
        value = fetch()
        if predicate(value):
            return value
        remaining = deadline - time.monotonic()
        assert remaining > 0, f'Timed out waiting for {description}'
        time.sleep(min(interval, remaining))


def submit_csv(context):
    s = state(context)
    assert s.csv_file is not None, 'Prepare the product CSV before uploading'
    s.response = api.upload_product_file(s.token, s.initiative_id, s.category, s.csv_file)
    return s.response


def completed_upload(context):
    s = state(context)
    filename = s.csv_file[0]
    matches = wait_for(
        lambda: [item for item in history(context) if item['fileName'] == filename],
        lambda items: len(items) == 1 and items[0]['uploadStatus'] in ('LOADED', 'PARTIAL'),
        f'CSV {filename} to finish processing',
    )
    s.upload = matches[0]
    return s.upload


def get_product(context, name):
    s = state(context)
    selected = s.products[name]
    previous_initiative = s.initiative_id
    # The producer view masks SUPERVISED/WAIT_APPROVED as UPLOADED and hides audit details.
    original_profile = getattr(s, 'profile', None)
    observer_required = s.role == 'operatore'
    if observer_required:
        authenticate(context, s.dataset.get('observer_profile', 'Invitalia'))
    s.initiative_id = selected['initiativeId']
    try:
        items = products(context, gtin_code=selected['gtinCode'])
    finally:
        s.initiative_id = previous_initiative
        if observer_required:
            authenticate(context, original_profile)
    assert len(items) == 1, f'Expected exactly one product {name}, got {len(items)}'
    return items[0]


def change_status(context, names, current_status, target_status):
    s = state(context)
    codes = [s.products[name]['gtinCode'] for name in names]
    if target_status == 'WAIT_APPROVED':
        return api.update_products_status_wait_approved(
            s.token, s.initiative_id, s.organization_id,
            s.products[names[0]]['organizationId'],
            s.bodies[s.profile].get('email', s.bodies[s.profile].get('orgEmail')),
            codes, current_status, 'RDB functional test', 'RDB functional test',
        )
    target = 'restored' if target_status == 'UPLOADED' else target_status.lower()
    return api.update_products_status(
        s.token, s.initiative_id, s.role, s.username, codes,
        current_status, target, 'RDB functional test', 'RDB functional test',
    )


def seed_product(context, name, status):
    """Create an isolated product through the existing upload/status APIs."""
    s = state(context)
    original_profile = s.profile
    producer_profile = original_profile if s.role == 'operatore' else s.dataset.get('producer_profile', 'producer')
    authenticate(context, producer_profile)
    set_csv(context)
    outcome(submit_csv(context))
    completed_upload(context)
    found = products(context, gtin_code=s.rows[0][0])
    assert len(found) == 1, f'Uploaded product {name} was not stored'
    assert found[0]['status'] == 'UPLOADED'
    s.products[name] = found[0]
    if status != 'UPLOADED':
        authenticate(context, 'Invitalia')
        intermediate = 'WAIT_APPROVED' if status == 'APPROVED' else status
        outcome(change_status(context, [name], 'UPLOADED', intermediate))
        if status == 'APPROVED':
            authenticate(context, 'Invitalia Admin')
            outcome(change_status(context, [name], intermediate, status))
    authenticate(context, original_profile)
    s.products[name] = get_product(context, name)
    assert s.products[name]['status'] == status
    s.before[name] = deepcopy(s.products[name])
    s.current_status = status
    return s.products[name]
