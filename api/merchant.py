import requests

from api.mock import put_mocked_visura_impresa
from model.visura_impresa import ClassificazioneAteco, InfoAttivita, VisuraImpresa
from conf.configuration import secrets
from conf.configuration import settings


def put_merchant(fiscal_code: str,
                 vat_number: str,
                 business_name: str,
                 acquirer_id: str,
                 iban: str,
                 iban_holder: str,
                 activation_date: str):
    return requests.put(
        f'{secrets.base_path.IDPAY.internal}'
        f'{settings.IDPAY.endpoints.merchant.internal_path}/merchant',
        headers={
            'Content-Type': 'application/json',
        },
        json={
            'fiscalCode': fiscal_code,
            'vatNumber': vat_number,
            'businessName': business_name,
            'acquirerId': acquirer_id,
            'iban': iban,
            'ibanHolder': iban_holder,
            'activationDate': activation_date,
        },
        timeout=settings.default_timeout
    )


def put_onboard_merchant_initiative(selfcare_token: str, 
                                    merchant_id: str, 
                                    initiative_id: str):
    return requests.put(
        url=f'{secrets.base_path.IO}'
        f'{settings.IDPAY.domain}'
        f'{settings.IDPAY.endpoints.ecommerce.merchant_portal}'
        f'/initiatives/{initiative_id}/onboarding',
        headers={
            'x-merchant-id': merchant_id,
            'Authorization': f'Bearer {selfcare_token}'
        },
        timeout=settings.default_timeout
    )


def exchange_selfcare_token_merchant_portal(selfcare_token: str):
    return requests.post(
        url=f'{secrets.base_path.IO}'
        f'{settings.IDPAY.domain}'
        f'{settings.IDPAY.endpoints.merchant.path}'
        "/token",
        headers={
            'Authorization': f'Bearer {selfcare_token}',
        },
        timeout=settings.default_timeout
    )


def get_merchant_initiatives_merchant_portal(merchant_token: str, merchant_id: str):
    return requests.get(
        url=f'{secrets.base_path.IO}'
        f'{settings.IDPAY.domain}'
        f'{settings.IDPAY.endpoints.ecommerce.merchant_portal}/initiatives',
        headers={
            'Authorization': f'Bearer {merchant_token}',
            'x-merchant-id': merchant_id,
        },
        timeout=settings.default_timeout
    )


def mock_merchant_ateco(fiscal_code: str, ateco: str):
    visura = VisuraImpresa(
        codice_fiscale=fiscal_code,
        info_attivita=InfoAttivita(
            classificazioni_ateco=[
                ClassificazioneAteco(
                    codice_attivita=ateco,
                    attivita=f'Attivita {ateco}',
                    codice_importanza='1'
                )
            ]
        )
    )

    response = put_mocked_visura_impresa(visura=visura)
    assert response.status_code in [200, 201, 204], (
        f'Failed to mock merchant ATECO for fiscal code {fiscal_code}: '
        f'status={response.status_code}, body={response.text}'
    )
    return response
