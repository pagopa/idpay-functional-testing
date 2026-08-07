import requests

from conf.configuration import secrets
from conf.configuration import settings
from util.asset_register_utilities import _build_csv_file_part

_AR = settings.IDPAY.endpoints.asset_register
_BASE = f'{secrets.base_path.IO}{settings.IDPAY.domain}'
_REGISTER_BASE = f'{_BASE}{_AR.internal_path}'

def _with_initiative_path(initiative_id: str, path_suffix: str) -> str:
    return f'{_REGISTER_BASE}{_AR.initiatives}/{initiative_id}{path_suffix}'

def post_token_test(body:dict):
    """ API to create token test of the asset register
        POST /idpay/register/test
        :param body: body of the request
    """
    return requests.post(f'{_REGISTER_BASE}{_AR.token_test}',
         headers={
             'Content-Type': 'application/json'
         },
        json=body,
        timeout = settings.default_timeout
    )

def get_portal_consent(token:str):
    """API to get the portal consent status for a user
        GET /idpay/consent
        :param token: bearer token
    """
    return requests.get(
        f'{_REGISTER_BASE}{_AR.consent.path}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        timeout=settings.default_timeout
    )

def save_portal_consent(token:str, version_id=None, first_acceptance=None):
    """API to save the portal consent for a user
        POST /idpay/consent
        :param token: bearer token
        :param version_id: accepted consent version id (optional)
        :param first_acceptance: whether this is the user's first acceptance (optional)
    """
    body = {}
    if version_id is not None:
        body['versionId'] = version_id
    if first_acceptance is not None:
        body['firstAcceptance'] = first_acceptance

    return requests.post(
        f'{_REGISTER_BASE}{_AR.consent.path}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        json=body,
        timeout=settings.default_timeout
    )

def get_initiatives(token:str):
    """API to get enabled initiatives for an organization
        :param token: bearer token
    """
    return requests.get(f'{_REGISTER_BASE}{_AR.initiatives}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        timeout=settings.default_timeout
    )

def verify_product_file(token:str, initiative_id:str, category:str, csv_file):
    """API to dry-run validate a product CSV file before uploading it
        POST /idpay/register/initiatives/{initiativeId}/product-files/verify
        :param token: bearer token
        :param initiative_id: initiative id
        :param category: ProductCategories value the file belongs to
        :param csv_file: CSV file to validate
    """
    return requests.post(
        _with_initiative_path(initiative_id, _AR.product_files.verify),
        headers={
            'Authorization': f'Bearer {token}'
        },
        params={'category': category},
        files={'csv': _build_csv_file_part(csv_file)},
        timeout=settings.default_timeout
    )

def upload_product_file(token:str, initiative_id:str, category:str, csv_file):
    """API to upload a product CSV file
        POST /idpay/register/initiatives/{initiativeId}/product-files
        :param token: bearer token
        :param initiative_id: initiative id
        :param category: ProductCategories value the file belongs to
        :param csv_file: CSV file to upload
    """
    return requests.post(
        _with_initiative_path(initiative_id, _AR.product_files.path),
        headers={
            'Authorization': f'Bearer {token}'
        },
        params={'category': category},
        files={'csv': _build_csv_file_part(csv_file)},
        timeout=settings.default_timeout
    )

def get_product_files(token:str, initiative_id:str, page=None, size=None):
    """API to get the paged list of uploaded product files
        GET /idpay/register/initiatives/{initiativeId}/product-files
        :param token: bearer token
        :param initiative_id: initiative id (mongo ObjectId)
        :param page: page number (optional)
        :param size: page size (optional, default 20 server-side)
    """
    params = {}
    if page is not None:
        params['page'] = page
    if size is not None:
        params['size'] = size

    return requests.get(
        _with_initiative_path(initiative_id, _AR.product_files.path),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        params=params,
        timeout=settings.default_timeout
    )

def download_product_file_report(token, initiative_id, product_file_id):
    """API to download the report generated for a product file upload
        GET /idpay/register/initiatives/{initiativeId}/product-files/{productFileId}/report
        :param token: bearer token
        :param initiative_id: initiative id
        :param product_file_id: product file id
    """
    return requests.get(
        _with_initiative_path(initiative_id, _AR.product_files.report.format(product_file_id)),
        headers={
            'Authorization': f'Bearer {token}',
        },
        timeout=settings.default_timeout
    )

def get_products(token,initiative_id:str, role='operatore', organization_id=None,
                  product_name=None, full_product_name=None, product_file_id=None,
                  eprel_code=None, gtin_code=None, product_code=None,
                  status=None, category=None, brand=None, model=None,
                  page=None, size=None, sort=None):
    """API to get the filtered/paged list of products
        GET /idpay/register/products
        NOTE: no initiativeId in the path — the initiative is derived from the JWT.
        :param token: bearer token
        :param initiative_id: initiative id
        :param role: organization role (defaults to 'operatore')
        :param organization_id: filter by organization uuid (optional)
        :param product_name: filter by product name (optional)
        :param full_product_name: filter by full product name (optional)
        :param product_file_id: filter by originating product file id (optional)
        :param eprel_code: filter by EPREL code (optional)
        :param gtin_code: filter by GTIN code (optional)
        :param product_code: filter by product code (optional)
        :param status: filter by ProductStatus (optional)
        :param category: filter by ProductCategories (optional)
        :param brand: filter by brand (optional)
        :param model: filter by model (optional)
        :param page: page number (optional)
        :param size: page size (optional, default 20 server-side)
        :param sort: sort clause (optional, default registrationDate,DESC server-side)
    """
    params = {}
    if organization_id is not None:
        params['organizationId'] = organization_id
    if product_name is not None:
        params['productName'] = product_name
    if full_product_name is not None:
        params['fullProductName'] = full_product_name
    if product_file_id is not None:
        params['productFileId'] = product_file_id
    if eprel_code is not None:
        params['eprelCode'] = eprel_code
    if gtin_code is not None:
        params['gtinCode'] = gtin_code
    if product_code is not None:
        params['productCode'] = product_code
    if status is not None:
        params['status'] = status
    if category is not None:
        params['category'] = category
    if brand is not None:
        params['brand'] = brand
    if model is not None:
        params['model'] = model
    if page is not None:
        params['page'] = page
    if size is not None:
        params['size'] = size
    if sort is not None:
        params['sort'] = sort

    return requests.get(
        _with_initiative_path(initiative_id, _AR.products.path),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'x-organization-role': role,
        },
        params=params,
        timeout=settings.default_timeout
    )


def get_product_files_batch_list(token, initiative_id, organization_selected=None):
    """API to get the distinct list of product file batches, filtered by role
        GET /idpay/register/initiatives/{initiativeId}/product-files/batch-list
        :param token: bearer token
        :param initiative_id: initiative id
        :param organization_selected: selected sub-organization uuid (optional)
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    if organization_selected is not None:
        headers['x-organization-selected'] = organization_selected

    return requests.get(
        _with_initiative_path(initiative_id, _AR.product_files.batch_list),
        headers=headers,
        timeout=settings.default_timeout
    )

def get_institution_by_id(token, institution_id):
    """API to get a single institution's details by id
        GET /idpay/register/institutions/{institutionId}
        :param token: bearer token
        :param institution_id: institution uuid
    """
    return requests.get(
        f'{_REGISTER_BASE}{_AR.institutions.by_id.format(institution_id)}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        timeout=settings.default_timeout
    )

_UPDATE_STATUS_TARGETS = ('approved', 'wait_approved', 'supervised', 'rejected', 'restored')
_UPDATE_STATUS_ENDPOINTS = {
    'approved': _AR.products.update_status.approved,
    'wait_approved': _AR.products.update_status.wait_approved,
    'wait-approved': _AR.products.update_status.wait_approved,
    'supervised': _AR.products.update_status.supervised,
    'rejected': _AR.products.update_status.rejected
}

def _build_products_update_body(gtin_codes, current_status, motivation=None, formal_motivation=None):
    body = {
        'gtinCodes': gtin_codes,
        'currentStatus': current_status,
    }
    if motivation is not None:
        body['motivation'] = motivation
    if formal_motivation is not None:
        body['formalMotivation'] = formal_motivation
    return body

def _update_products_status_request(token, initiative_id, role, username, endpoint_path, gtin_codes, current_status,
                                    motivation=None, formal_motivation=None):
    return requests.post(
        _with_initiative_path(initiative_id, endpoint_path),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'x-organization-role': role,
            'x-user-name': username,
        },
        json=_build_products_update_body(gtin_codes, current_status, motivation, formal_motivation),
        timeout=settings.default_timeout
    )

def update_products_status_approved(token, initiative_id, role, username, gtin_codes, current_status,
                                    motivation=None, formal_motivation=None):
    """POST /idpay/register/initiatives/{initiativeId}/products/update-status/approved"""
    return _update_products_status_request(
        token, initiative_id, role, username, _AR.products.update_status.approved,
        gtin_codes, current_status, motivation, formal_motivation
    )

def update_products_status_wait_approved(token,initiative_id, organization_id, organization_selected, user_email,
                                         gtin_codes, current_status, motivation=None, formal_motivation=None):
    """POST /idpay/register/initiatives/{initiativeId}/products/update-status/wait-approved"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'x-organization-id': organization_id,
        'x-organization-selected': organization_selected,
        'x-user-email': user_email,
    }
    return requests.post(
        _with_initiative_path(initiative_id, _AR.products.update_status.wait_approved),
        headers=headers,
        json=_build_products_update_body(gtin_codes, current_status, motivation, formal_motivation),
        timeout=settings.default_timeout
    )

def update_products_status_supervised(token, initiative_id, role, username, gtin_codes, current_status,
                                      motivation=None, formal_motivation=None):
    """POST /idpay/register/initiatives/{initiativeId}/products/update-status/supervised"""
    return _update_products_status_request(
        token, initiative_id, role, username, _AR.products.update_status.supervised,
        gtin_codes, current_status, motivation, formal_motivation
    )

def update_products_status_rejected(token, initiative_id, role, username, gtin_codes, current_status,
                                    motivation=None, formal_motivation=None):
    """POST /idpay/register/initiatives/{initiativeId}/products/update-status/rejected"""
    return _update_products_status_request(
        token, initiative_id, role, username, _AR.products.update_status.rejected,
        gtin_codes, current_status, motivation, formal_motivation
    )

def update_products_status(token, initiative_id, role, username, gtin_codes, current_status, target_status,
                           motivation=None, formal_motivation=None):
    """API to bulk update product status selecting one of the dedicated per-status endpoints.

        :param token: bearer token
        :param initiative_id: initiative id
        :param role: organization role
        :param username: acting user's name (audit trail)
        :param gtin_codes: list of GTIN codes to update
        :param current_status: expected current ProductStatus (ProductsUpdateDTO)
        :param target_status: one of 'approved' | 'wait_approved' | 'wait-approved' | 'supervised' | 'rejected' | 'restored'
        :param motivation: motivation shown/stored for the change (optional)
        :param formal_motivation: formal motivation shown/stored for the change (optional)
    """
    endpoint_path = _UPDATE_STATUS_ENDPOINTS.get(target_status)
    if endpoint_path is None:
        raise ValueError(
            f"target_status must be one of {tuple(_UPDATE_STATUS_ENDPOINTS.keys())}, got {target_status!r}"
        )

    return _update_products_status_request(
        token, initiative_id, role, username, endpoint_path,
        gtin_codes, current_status, motivation, formal_motivation
    )

def get_producers(token, initiative_id, page=None, size=None, sort=None):
    """API to get producers registered on an initiative
        GET /idpay/register/initiatives/{initiativeId}/producers
        :param token: bearer token
        :param initiative_id: initiative to fetch producers for
        :param page: page number (optional)
        :param size: page size (optional, default 1000 server-side)
        :param sort: sort clause (optional)
    """
    params = {}
    if page is not None:
        params['page'] = page
    if size is not None:
        params['size'] = size
    if sort is not None:
        params['sort'] = sort

    return requests.get(
         _with_initiative_path(initiative_id, _AR.producers),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        },
        params=params,
        timeout=settings.default_timeout
    )

def update_operative_email(token, organization_id, initiative_id, operative_email):
    """API to update the operative email for an organization on an initiative

        UNCONFIRMED against the public OpenAPI spec — not present there.
        Kept as implemented in ProducerImportController:
        PUT /idpay/register/initiatives/{initiativeId}/email.

        :param token: bearer token
        :param organization_id: organization uuid
        :param initiative_id: initiative id (mongo ObjectId)
        :param operative_email: new operative email
    """
    return requests.put(
        _with_initiative_path(initiative_id, _AR.email),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'x-organization-id': organization_id,
        },
        json={
            'operativeEmail': operative_email
        },
        timeout=settings.default_timeout
    )