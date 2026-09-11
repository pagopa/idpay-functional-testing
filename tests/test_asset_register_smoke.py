"""Smoke tests for Asset Register endpoints.
"""

from api.asset_register import *
from util.asset_register_utilities import build_operatore_token_body, build_l2_token_body, fake_product_file, \
    build_l1_token_body
import pytest

TOKEN = None

@pytest.fixture(scope="module", autouse=True)
def setup_once():
    print("setup iniziale")
    global TOKEN
    body = build_operatore_token_body()
    token_response = post_token_test(body=body)

    print(token_response.request.url)
    print("status:", token_response.status_code)
    print("raw body:", token_response.text)  # qui vedi cosa torna davvero l'endpoint
    TOKEN = token_response.text.strip().strip('"')
    assert token_response.status_code == 200, (
        f'response status code: {token_response.status_code}, and body {token_response.json()}'
    )

def _assert_endpoint_responded(response):
    assert response.status_code == 200, (
        f'response status code: {response.status_code}, and body {response.json()}'
    )
    assert response.status_code < 500, (
        f'Endpoint did not respond correctly: status={response.status_code}, body={response.text}'
    )


def _assert_update_status_endpoint_responded(response):
    assert response.status_code in (200, 400, 401, 429), (
        f'Unexpected status code for update-status endpoint: {response.status_code}, body={response.text}'
    )
    assert response.status_code < 500, (
        f'Endpoint did not respond correctly: status={response.status_code}, body={response.text}'
    )


def _assert_product_file_endpoint_responded(response):
    assert response.status_code in (200, 400, 401, 429), (
        f'Unexpected status code for product-file endpoint: {response.status_code}, body={response.text}'
    )
    assert response.status_code < 500, (
        f'Endpoint did not respond correctly: status={response.status_code}, body={response.text}'
    )


def _assert_download_report_endpoint_responded(response):
    assert response.status_code in (200, 400, 401, 404, 429), (
        f'Unexpected status code for product-file report endpoint: {response.status_code}, body={response.text}'
    )
    assert response.status_code < 500, (
        f'Endpoint did not respond correctly: status={response.status_code}, body={response.text}'
    )


def _assert_update_operative_email_endpoint_responded(response):
    assert response.status_code in (200, 400, 401, 403, 404, 429), (
        f'Unexpected status code for update operative email endpoint: {response.status_code}, body={response.text}'
    )
    assert response.status_code < 500, (
        f'Endpoint did not respond correctly: status={response.status_code}, body={response.text}'
    )


def _get_available_initiative_id():
    initiatives = getattr(secrets, 'initiatives', None)
    if not initiatives:
        pytest.skip('No initiatives available in secrets')

    preferred_initiatives = ('bonus_elettrodomestici')
    for initiative_name in preferred_initiatives:
        if initiative_name in initiatives and 'id' in initiatives[initiative_name]:
            return initiatives[initiative_name]['id']

    for initiative in initiatives.values():
        if isinstance(initiative, dict) and 'id' in initiative:
            return initiative['id']

    pytest.skip('No initiative id available in secrets.initiatives')


def _get_l2_token():
    body = build_l2_token_body()
    token_response = post_token_test(body=body)
    _assert_endpoint_responded(token_response)
    return token_response.text.strip().strip('"')


def _get_product_update_context(token, initiative_id):
    products_response = get_products(token=token, initiative_id=initiative_id, page=0, size=1)
    _assert_endpoint_responded(products_response)
    products_payload = products_response.json()
    products = products_payload.get('content') if isinstance(products_payload, dict) else products_payload

    if not products:
        pytest.skip('No products available for update-status smoke tests')

    first_product = products[0]
    gtin_code = first_product.get('gtinCode') or first_product.get('gtin')
    current_status = first_product.get('status') or first_product.get('productStatus')
    if not gtin_code or not current_status:
        pytest.skip(f'Product payload does not include gtin/status: {first_product}')
    return gtin_code, current_status


def _get_product_file_id_for_initiative(initiative_id):
    response = get_product_files(token=TOKEN, initiative_id=initiative_id, page=0, size=1)
    _assert_endpoint_responded(response)
    payload = response.json()
    product_files = payload.get('content') if isinstance(payload, dict) else payload
    if not product_files:
        pytest.skip('No product files available for report/download smoke tests')
    first_file = product_files[0]
    product_file_id = first_file.get('id') or first_file.get('productFileId') or first_file.get('batchId')
    if not product_file_id:
        pytest.skip(f'Product file payload does not include a file id: {first_file}')
    return product_file_id


def test_get_initiatives_responds():

    response = get_initiatives(token=TOKEN)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_endpoint_responded(response)


def test_get_products_responds():
    body = build_l2_token_body()
    token_response = post_token_test(body=body)
    response = get_products(token=token_response.text.strip().strip('"'), initiative_id="68dd003ccce8c534d1da22bc", page=0, size=1)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_endpoint_responded(response)


def test_get_product_files_responds():
    initiative_id = _get_available_initiative_id()
    response = get_product_files(token=TOKEN, initiative_id=initiative_id, page=0, size=1)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_endpoint_responded(response)


def test_get_product_files_batch_list_responds():
    initiative_id = _get_available_initiative_id()
    response = get_product_files_batch_list(token=TOKEN, initiative_id=initiative_id)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_endpoint_responded(response)


def test_get_producers_responds():
    body = build_l2_token_body()
    token_response = post_token_test(body=body)
    initiative_id = _get_available_initiative_id()
    response = get_producers(token=token_response.text.strip().strip('"'), initiative_id=initiative_id, page=0, size=1)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_endpoint_responded(response)


def test_get_portal_consents_responds():
    response = get_portal_consent(token=TOKEN)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_endpoint_responded(response)

def test_save_portal_consent():
    response = save_portal_consent(token=TOKEN, version_id="test", first_acceptance=True )
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_endpoint_responded(response)

def test_verify_product_files_responds():
    initiative_id = _get_available_initiative_id()
    fake_csv_file = fake_product_file()

    response = verify_product_file(token=TOKEN, initiative_id=initiative_id, category="RANGEHOODS", csv_file=fake_csv_file)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_product_file_endpoint_responded(response)


def test_upload_product_file_responds():
    initiative_id = _get_available_initiative_id()
    fake_csv_file = fake_product_file()

    response = upload_product_file(token=TOKEN, initiative_id=initiative_id, category="RANGEHOODS", csv_file=fake_csv_file)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_product_file_endpoint_responded(response)


def test_download_product_file_report_responds():
    initiative_id = _get_available_initiative_id()
    product_file_id = _get_product_file_id_for_initiative(initiative_id)
    response = download_product_file_report(token=TOKEN, initiative_id=initiative_id, product_file_id=product_file_id)
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_download_report_endpoint_responded(response)

def test_get_institution_by_id_responds():
    body = build_l1_token_body()
    token_response = post_token_test(body=body)
    #response = get_institution_by_id(token=token_response.text, institution_id="72c2c5f8-1c71-4614-a4b3-95e3aee71c3d")
    response = get_institution_by_id(token=token_response.text, institution_id="762d5dc0-3ac6-4a61-b823-7e03e90ca52b")
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_endpoint_responded(response)


def test_update_operative_email_responds():
    initiative_id = _get_available_initiative_id()
    l2_token = _get_l2_token()
    organization_id = build_l2_token_body()["orgId"]
    response = update_operative_email(
        token=l2_token,
        organization_id=organization_id,
        initiative_id=initiative_id,
        operative_email='test.rdb.dev+smoke@gmail.com'
    )
    print(response.request.url)
    print("status:", response.status_code)
    print("raw body:", response.text)
    _assert_update_operative_email_endpoint_responded(response)

def test_update_products_status_responds():
    initiative_id = _get_available_initiative_id()
    token = _get_l2_token()
    gtin_code, current_status = _get_product_update_context(token, initiative_id)
    response = update_products_status(
        token=token,
        initiative_id=initiative_id,
        role='invitalia_admin',
        username='smoke-test',
        gtin_codes=[gtin_code],
        current_status=current_status,
        target_status='approved',
    )
    _assert_update_status_endpoint_responded(response)


def test_update_products_status_approved_responds():
    initiative_id = _get_available_initiative_id()
    token = _get_l2_token()
    gtin_code, current_status = _get_product_update_context(token, initiative_id)
    response = update_products_status_approved(
        token=token,
        initiative_id=initiative_id,
        role='invitalia_admin',
        username='smoke-test',
        gtin_codes=[gtin_code],
        current_status=current_status,
    )
    _assert_update_status_endpoint_responded(response)


def test_update_products_status_wait_approved_responds():
    initiative_id = _get_available_initiative_id()
    body = build_l1_token_body()
    token_response = post_token_test(body=body)
    response = update_products_status_wait_approved(
        token=token_response.text,
        initiative_id=initiative_id,
        organization_id='b5ae0b41-b854-414e-8295-078595ee1db4',
        organization_selected='b5ae0b41-b854-414e-8295-078595ee1db4',
        user_email='test',
        gtin_codes=['COOKINGHOBS04'],
        current_status='UPLOADED',
        motivation='motivation'
    )
    _assert_update_status_endpoint_responded(response)


def test_update_products_status_supervised_responds():
    initiative_id = _get_available_initiative_id()
    body = build_l1_token_body()
    token_response = post_token_test(body=body)
    response = update_products_status_supervised(
        token=token_response.text,
        initiative_id=initiative_id,
        role='invitalia',
        username='smoke-test',
        gtin_codes=['2068977'],
        current_status='SUPERVISED',
        motivation='motivation')
    _assert_update_status_endpoint_responded(response)


def test_update_products_status_rejected_responds():
    initiative_id = _get_available_initiative_id()
    body = build_l1_token_body()
    token_response = post_token_test(body=body)

    response = update_products_status_rejected(
        token=token_response.text,
        initiative_id=initiative_id,
        role='invitalia',
        username='smoke-test',
        gtin_codes=['COOKINGHOBS01'],
        current_status='UPLOADED',
        motivation='motivation'
    )
    _assert_update_status_endpoint_responded(response)
