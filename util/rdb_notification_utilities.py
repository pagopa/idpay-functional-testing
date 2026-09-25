"""Build explicit test payloads for the email service acceptance contract."""
import json
import uuid

from api import idpay
from conf.configuration import secrets
from conf.configuration import settings
from util import rdb_utilities as rdb


# Templates and subjects from the RDB backend application.yml.
TEMPLATES = {
    'ok': ('Email_RDB_EsitoProdottiOK', 'Prodotti elaborati con successo'),
    'partial': ('Email_RDB_EsitoProdottiParziale', 'Elaborazione parziale dei prodotti'),
    'rejected': ('Email_RDB_EsclusioneProdotti',
                 'Notifica di esclusione prodotto - Elenco informatico degli elettrodomestici'),
}


def service_config():
    return rdb.required(rdb.config(), 'email_service', 'secrets.asset_register')


def request_headers():
    config = service_config()
    headers = dict(config.get('headers') or {})
    authentication = config.get('authentication')
    assert authentication in (None, 'portal'), 'Unsupported email service authentication'
    if authentication == 'portal':
        token = rdb.token_from_response(idpay.obtain_selfcare_test_token(secrets.selfcare_info.test_institution))
        headers['Authorization'] = f'Bearer {token}'
    return headers


def request_payload(kind):
    config = service_config()
    # Require an explicit test destination before making any service call.
    recipient = rdb.required(config, 'test_recipient', 'asset_register.email_service')
    template, subject = TEMPLATES[kind]
    marker = f'rdb-contract-{uuid.uuid4().hex}'
    environment = str(settings.TARGET_ENV).lower()
    portal_url = settings.RDB_EMAIL_PORTAL_URLS.get(environment)
    assert portal_url, f'Missing RDB_EMAIL_PORTAL_URLS.{environment} in settings'
    values = {'initiativeName': config.get('initiative_name', 'RDB functional test'),
              'portalUrl': portal_url}
    if kind == 'rejected':
        values.update(excludedList=f'<li>{marker}</li>', formalMotivation='Functional test')
    else:
        values['productFileName'] = f'{marker}.csv'
    return {'templateName': template, 'templateValues': values, 'subject': subject,
            'content': None, 'senderEmail': None, 'recipientEmail': recipient}


def describe_request(payload):
    """Show the template inputs without credentials or the recipient address."""
    return json.dumps({**payload, 'recipientEmail': '<configured test recipient>'},
                      ensure_ascii=False, indent=2)


def describe_error(response):
    """Expose the service error, excluding arbitrary response fields and headers."""
    try:
        body = response.json()
    except ValueError:
        return 'No JSON error body'
    if not isinstance(body, dict):
        return 'No JSON error object'
    return json.dumps({key: body[key] for key in ('code', 'message') if key in body},
                      ensure_ascii=False)
