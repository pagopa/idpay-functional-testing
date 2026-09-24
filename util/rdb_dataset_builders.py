"""Prepare fixtures through real APIs, reusing existing inventories for read tests."""
import re
import uuid
from copy import deepcopy
from datetime import date, timedelta

from api import asset_register as api
from api import idpay
from conf.configuration import secrets
from util import rdb_utilities as rdb


def new_producer(context, aliases=('A',), email=None):
    s = rdb.state(context)
    body = deepcopy(rdb.build_operatore_token_body())
    body.update(orgId=str(uuid.uuid4()), uid=str(uuid.uuid4()), orgName='RDB dataset producer')
    profile = f'dataset producer {body["orgId"]}'
    associations = []
    for alias in aliases:
        associations.append({'initiativeId': rdb.select_initiative(context, alias),
                             'producerId': body['orgId'], 'producerName': body['orgName'],
                             'producerEmail': email})
    result = rdb.outcome(api.import_producers(associations))
    assert (result['totalRecords'], result['importedRecords'], result['failedRecords']) == (
        len(associations), len(associations), 0), 'Dataset producer import was incomplete'
    s.bodies[profile] = body
    s.tokens[profile] = rdb.get_rdb_access_token(body)
    rdb.authenticate(context, profile)
    rdb.select_initiative(context, aliases[0])
    return profile, [item['initiativeId'] for item in associations]


def finish_upload(context):
    rdb.outcome(rdb.submit_csv(context))
    upload = rdb.completed_upload(context)
    assert upload['uploadStatus'] == 'LOADED', 'Dataset CSV was not completely loaded'
    return upload


def enabled_initiatives(context):
    # A/B and the producer are explicitly configured fixtures. Keep exact-set
    # assertions: additional associations must fail, not become expected via a read.
    rdb.authenticate(context, 'producer')
    ids = [rdb.select_initiative(context, alias) for alias in ('A', 'B')]
    assert len(set(ids)) == 2, 'Dataset requires two distinct initiatives'
    return {'profile': 'producer', 'initiative': 'A', 'initiative_ids': ids}


def unassociated_initiative(context):
    rdb.select_initiative(context, 'A')
    rdb.authenticate(context, 'producer')
    # A must really exist: unknown IDs would exercise a different error.
    assert any(x['initiativeId'] == context.rdb.initiative_id
               for x in rdb.success(api.get_initiatives(context.rdb.token)).json())
    rdb.producer_without_initiatives(context)
    return {'profile': context.rdb.profile, 'initiative': 'A'}


def institution(context, unauthorized=False):
    producer = rdb.build_operatore_token_body()
    institution_id = producer['orgId']
    expected = {'vatNumber': producer['orgVat'], 'description': producer['orgName']}
    rdb.authenticate(context, 'Invitalia')
    if unauthorized:
        body = rdb.success(api.get_institution_by_id(context.rdb.token, institution_id)).json()
        rdb.assert_institution_details(body, expected)
    return {'profile': 'producer' if unauthorized else 'Invitalia', 'institution_id': institution_id,
            'institution_expected': expected}


def product_batch_ids(products):
    """ProductMapper exposes the file ObjectId as the suffix of batchName."""
    ids = set()
    for product in products:
        match = re.search(r'_([0-9a-fA-F]{24})\.csv$', product.get('batchName') or '')
        assert match, 'Product batchName must contain the originating CSV ObjectId'
        ids.add(match.group(1))
    return sorted(ids)


def scoped_records(context, kind):
    """Compare filtered/role-specific reads with an unfiltered Invitalia inventory.

    These checks prove consistency and scope, not independent inventory completeness.
    No imports or CSV uploads are needed; missing exclusion controls fail explicitly.
    """
    organization = rdb.build_operatore_token_body()['orgId']
    rdb.authenticate(context, 'Invitalia')
    inventories = {}
    initiative_ids = []
    for alias in ('A', 'B'):
        initiative = rdb.select_initiative(context, alias)
        initiative_ids.append(initiative)
        inventories[alias] = rdb.products(context)
        assert inventories[alias], f'Read fixture requires existing products in initiative {alias}'
        assert all(p['initiativeId'] == initiative for p in inventories[alias]), (
            f'Product list returned records outside initiative {alias}')
    assert len(set(initiative_ids)) == 2, 'Read fixture requires two distinct initiatives'

    own = [p for p in inventories['A'] if p['organizationId'] == organization]
    foreign = [p for p in inventories['A'] if p['organizationId'] != organization]
    assert own, 'Read fixture requires existing products for the configured producer in A'
    assert foreign, 'Read fixture requires products of another organization in A'
    profile = 'producer'
    selected = own
    if kind in ('Invitalia registry', 'foreign CSV batches'):
        profile = 'Invitalia'
        organization = sorted({p['organizationId'] for p in foreign})[0]
        selected = [p for p in foreign if p['organizationId'] == organization]
    data = {'profile': profile, 'initiative': 'A', 'organization_id': organization,
            'product_gtins': [p['gtinCode'] for p in selected]}
    if kind == 'CSV history':
        data.update(known_upload_ids=product_batch_ids(own),
                    foreign_upload_ids=product_batch_ids(foreign + inventories['B']))
        assert set(data['known_upload_ids']).isdisjoint(data['foreign_upload_ids']), (
            'CSV isolation controls overlap across organizations or initiatives')
    elif kind in ('organization CSV batches', 'foreign CSV batches'):
        data['batch_ids'] = product_batch_ids(selected)
    return data


def inaccessible_report(context, other_initiative=False):
    s = rdb.state(context)
    if other_initiative:
        # Report access is scoped by organization AND initiative. Reuse the
        # configured producer, but prove it is enabled on both initiatives.
        rdb.authenticate(context, 'producer')
        ids = {rdb.select_initiative(context, alias) for alias in ('A', 'B')}
        assert len(ids) == 2, 'Report isolation requires two distinct initiatives'
        enabled = {item['initiativeId'] for item in rdb.success(api.get_initiatives(s.token)).json()
                   if item['enabled'] is True}
        assert ids <= enabled, 'The configured producer must be enabled on A and B'
        rdb.select_initiative(context, 'A')
    else:
        rdb.authenticate(context, 'producer')
        rdb.select_initiative(context, 'A')
    rows = rdb.cooking_products()
    rows[0][0] = ''
    rdb.set_csv(context, rows)
    result = rdb.outcome(api.verify_product_file(s.token, s.initiative_id, s.category, s.csv_file), 'KO')
    assert result['errorKey'] == 'product.invalid.file.report'
    file_id = result['productFileId']
    # Demonstrate report existence before testing access from a different scope.
    rdb.success(api.download_product_file_report(s.token, s.initiative_id, file_id))
    if other_initiative:
        rdb.select_initiative(context, 'B')
    else:
        owner = s.organization_id
        # DownloadReport checks the report's organization and initiative, without
        # an association precondition. A fresh producer token is sufficient.
        rdb.producer_without_initiatives(context)
        assert s.organization_id != owner
    return {'profile': s.profile, 'initiative': 'B' if other_initiative else 'A',
            'product_file_id': file_id}


def producer_without_email(context):
    profile, _ = new_producer(context)
    return {'profile': profile, 'initiative': 'A', 'producer_profile': profile}


def initiative_producers(context):
    """Known memberships come from initiative and product APIs, not the producer list."""
    rdb.authenticate(context, 'producer')
    initiative = rdb.select_initiative(context, 'A')
    s = rdb.state(context)
    enabled = rdb.success(api.get_initiatives(s.token)).json()
    assert any(i['initiativeId'] == initiative and i['enabled'] for i in enabled), (
        'The configured producer must be enabled on initiative A')
    organization = s.organization_id
    rdb.authenticate(context, 'Invitalia')
    products = rdb.products(context)
    assert products, 'Producer list verification requires known products in A'
    assert all(p['initiativeId'] == initiative for p in products)
    return {'profile': 'Invitalia', 'initiative': 'A',
            'known_producer_ids': sorted({organization, *(p['organizationId'] for p in products)})}


def portal_initiatives(context, foreign=False):
    """Create portal initiatives owned by fresh organizations, with an exclusion control.

    InitiativeService delegates the Invitalia view to the portal summary API.
    Expected IDs come from acknowledged POST /initiative/info writes, not reads.
    Draft initiatives are included by that summary and map to enabled=True in RDB.
    """
    s = rdb.state(context)
    organizations = [str(uuid.uuid4()), str(uuid.uuid4())]
    expected = []
    for index, organization in enumerate(organizations):
        portal_body = deepcopy(secrets.selfcare_info.test_institution)
        portal_body.update(orgId=organization, uid=str(uuid.uuid4()),
                           orgName='RDB initiative dataset', email='rdb-functional-test@example.com')
        portal_token = rdb.token_from_response(idpay.obtain_selfcare_test_token(portal_body))
        count = 2 if index == 0 and not foreign else 1
        created = []
        for _ in range(count):
            result = rdb.success(idpay.post_initiative_info(
                portal_token, initiative_name_prefix=f'RDB fixture {uuid.uuid4().hex}'), 201).json()
            initiative_id = rdb.required(result, 'initiativeId', 'portal creation response')
            # Portal summary dereferences general.startDate/endDate even for drafts.
            general = {'beneficiaryType': 'PF', 'beneficiaryKnown': False,
                       'rankingEnabled': False, 'budget': 1000, 'beneficiaryBudgetFixed': 100,
                       'startDate': (date.today() + timedelta(days=1)).isoformat(),
                       'endDate': (date.today() + timedelta(days=30)).isoformat(),
                       'descriptionMap': {'it': 'RDB isolated initiative fixture'}}
            rdb.success(idpay.put_initiative_general_info(portal_token, initiative_id, general), 204)
            created.append(initiative_id)
            if index == 0:
                expected.append(initiative_id)
        # Verify fixture readiness through the source portal; expected IDs still
        # come solely from our writes, not from the RDB endpoint under test.
        summary = rdb.success(idpay.get_initiatives_summary(portal_token)).json()
        assert sorted(item['initiativeId'] for item in summary) == sorted(created)
    body = deepcopy(rdb.build_l1_token_body())
    body.update(orgId=organizations[0], uid=str(uuid.uuid4()), orgName='RDB initiative dataset')
    profile = f'Invitalia initiative dataset {organizations[0]}'
    s.bodies[profile] = body
    s.tokens[profile] = rdb.get_rdb_access_token(body)
    return {'profile': profile, 'initiative_ids': expected}


def product_filters(context):
    s = rdb.state(context)
    producer = 'producer'
    rdb.authenticate(context, producer)
    organization = s.organization_id
    rows = rdb.cooking_products(4)
    # ProductSpecificRepositoryImpl applies substring matching to gtinCode.
    # Scope every query to these five inputs while keeping category/status
    # exclusion controls, without importing another organization.
    gtin_prefix = uuid.uuid4().hex[:12]
    marker = uuid.uuid4().hex
    for index, row in enumerate(rows):
        row[0] = f'{gtin_prefix}{index:02x}'
        row[4], row[5] = f'Brand {marker}', f'Model {marker}'
    rows[1][4] = f'Other {marker}'
    rows[2][5] = f'Other {marker}'
    upload = rdb.upload_generated_csv(context, rows)
    rdb.eprel_csv(context, 'valid')
    assert len(s.rows) == 1, 'Product filters require exactly one valid EPREL control row'
    s.rows[0][s.headers.index('Codice GTIN/EAN')] = f'{gtin_prefix}04'
    rdb.set_csv(context, s.rows, s.headers, s.category)
    eprel_code, eprel_gtin = s.rows[0][:2]
    finish_upload(context)
    # Preserve a status control visible in the Invitalia view.
    s.products['status control'] = {'gtinCode': rows[3][0], 'organizationId': organization}
    rdb.authenticate(context, 'Invitalia')
    rdb.outcome(rdb.change_status(context, ['status control'], 'UPLOADED', 'SUPERVISED'))
    return {'profile': 'Invitalia', 'initiative': 'A', 'producer_profile': producer,
            'query_scope': {'organization_id': organization, 'gtin_code': gtin_prefix},
            'filters': {'category': 'COOKINGHOBS', 'status': 'UPLOADED',
                        'EPREL code': eprel_code, 'brand': rows[0][4], 'model': rows[0][5],
                        'CSV upload': upload['productFileId'], 'GTIN': rows[0][0], 'product name': marker},
            'filter_product_gtins': {
                'category': [row[0] for row in rows],
                'status': [row[0] for row in rows[:3]] + [eprel_gtin],
                'EPREL code': [eprel_gtin],
                'CSV upload': [row[0] for row in rows],
                'GTIN': [rows[0][0]],
                'brand': [rows[i][0] for i in (0, 2, 3)],
                'model': [rows[i][0] for i in (0, 1, 3)],
                'product name': [row[0] for row in rows],
                'category, brand, model, status': [rows[0][0]],
            }}


BUILDERS = {
    'producer enabled initiatives': enabled_initiatives,
    'unassociated initiative': unassociated_initiative,
    'SelfCare producer': institution,
    'unauthorized producer details': lambda c: institution(c, unauthorized=True),
    'producer registry': lambda c: scoped_records(c, 'producer registry'),
    'Invitalia registry': lambda c: scoped_records(c, 'Invitalia registry'),
    'CSV history': lambda c: scoped_records(c, 'CSV history'),
    'organization CSV batches': lambda c: scoped_records(c, 'organization CSV batches'),
    'foreign CSV batches': lambda c: scoped_records(c, 'foreign CSV batches'),
    'report from another producer': inaccessible_report,
    'report from another initiative': lambda c: inaccessible_report(c, other_initiative=True),
    'producer without email': producer_without_email,
    'initiative producers': initiative_producers,
    'product filters': product_filters,
    'Invitalia organization initiatives': portal_initiatives,
    'Invitalia foreign initiative': lambda c: portal_initiatives(c, foreign=True),
}
