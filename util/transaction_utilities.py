import datetime
import time

from api.idpay import obtain_merchant_test_token
from api.transaction import get_merchant_transactions_processed, get_reports, get_report_download
from api.transaction import post_approve_transactions
from api.transaction import post_reject_transactions
from api.transaction import post_suspend_transactions
from api.transaction import post_validate_reward_batch
from conf.configuration import secrets
from conf.configuration import settings
from model.transaction_model import ChecksErrorDTO, ReportRequest
from model.transaction_model import TransactionActionRequest
from util.utility import get_selfcare_token
from util.utility import retry_reward_batch_eligibility

MERCHANT_TOKEN_AUD = 'idpay.merchant.welfare.pagopa.it'
DEFAULT_POINT_OF_SALE_ID = '1234'


def _get_institution_token_profile(role: str) -> dict[str, str]:
    institution = getattr(secrets, 'institution', None)
    if institution is None:
        raise KeyError('Missing secrets.institution configuration')

    payload = institution.get(role)
    if payload is None:
        raise KeyError(f"Missing secrets.institution.{role} configuration")

    return payload


def _build_merchant_token_body(role: str) -> dict[str, str]:
    institution_profile = _get_institution_token_profile(role)

    return {
        'aud': institution_profile['aud'],
        'iss': institution_profile['iss'],
        'uid': institution_profile['uid'],
        'name': institution_profile['name'],
        'familyName': institution_profile['family_name'],
        'email': institution_profile['email'],
        'acquirerId': settings.idpay.acquirer_id,
        'merchantId': secrets.organization_id,
        'orgId': institution_profile['org_id'],
        'orgVAT': institution_profile['org_vat'],
        'orgName': institution_profile['org_name'],
        'orgPartyRole': institution_profile['org_party_role'],
        'orgRole': institution_profile['org_role'],
        'pointOfSaleId': DEFAULT_POINT_OF_SALE_ID,
    }


def build_l1_token_body() -> dict[str, str]:
    return _build_merchant_token_body(role='l1')


def build_l2_token_body() -> dict[str, str]:
    return _build_merchant_token_body(role='l2')


def build_l3_token_body() -> dict[str, str]:
    return _build_merchant_token_body(role='l3')


def get_institutions_access_token(role: str = 'l1') -> str:
    response = obtain_merchant_test_token(_build_merchant_token_body(role=role))
    assert response.status_code == 200, (
        f"Instititution test token failed: {response.status_code} {response.text}"
    )
    access_token = response.text
    assert access_token
    return access_token


def get_institution_selfcare_token(role: str) -> str:
    token_body_by_role = {
        'l1': build_l1_token_body,
        'l2': build_l2_token_body,
        'l3': build_l3_token_body,
    }
    build_token_body = token_body_by_role.get(role)
    if build_token_body is None:
        raise ValueError(f"Unsupported role action: {role}")
    return get_selfcare_token(build_token_body())


def assert_transaction_in_processed_reward_batch(merchant_id: str,
                                                 initiative_id: str,
                                                 access_token: str,
                                                 reward_batch_id: str,
                                                 transaction_id: str):
    response = get_merchant_transactions_processed(
        merchant_id=merchant_id,
        initiative_id=initiative_id,
        access_token=access_token,
        reward_batch_id=reward_batch_id,
    )
    assert response.status_code == 200, (
        f"Processed transactions request failed: {response.status_code} {response.text}"
        f"request: {response.request.url}"
    )
    assert any(
        trx['trxId'].strip() == transaction_id.strip()
        for trx in response.json().get('content', [])
    ), f"Transaction {transaction_id} not found in reward batch {reward_batch_id}"


def perform_reward_batch_transaction_action(initiative_id: str,
                                            reward_batch_id: str,
                                            access_token: str,
                                            transaction_id: str,
                                            transaction_action: str):
    action_requests = {
        'approve': TransactionActionRequest(transaction_ids=[transaction_id]),
        'reject': TransactionActionRequest(
            transaction_ids=[transaction_id],
            reason='Rejected by operator',
            checks_error=ChecksErrorDTO(price_error=True),
        ),
        'suspend': TransactionActionRequest(
            transaction_ids=[transaction_id],
            reason='Suspended by operator',
            checks_error=ChecksErrorDTO(generic_error=True),
        ),
    }
    transaction_action_request = action_requests.get(transaction_action)
    if transaction_action_request is None:
        raise ValueError(f"Unsupported transaction action: {transaction_action}")

    action_calls = {
        'approve': post_approve_transactions,
        'reject': post_reject_transactions,
        'suspend': post_suspend_transactions,
    }
    action_response = action_calls[transaction_action](
        initiative_id=initiative_id,
        reward_batch_id=reward_batch_id,
        access_token=access_token,
        transaction_action_request=transaction_action_request,
    )
    assert action_response.status_code == 200, (
        f"Reward batch transaction action '{transaction_action}' failed: "
        f"{action_response.status_code} {action_response.text}"
    )
    return action_response


def validate_reward_batch_as_operator(initiative_id: str,
                                      reward_batch_id: str,
                                      access_token: str):
    validate_reward_batch_response = post_validate_reward_batch(
        initiative_id,
        reward_batch_id,
        access_token
    )
    assert validate_reward_batch_response.status_code == 200, (
        f"Reward batch validation failed: "
        f"{validate_reward_batch_response.status_code} {validate_reward_batch_response.text}"
        f"token: {access_token}"
    )


def request_reward_batch_validation(initiative_id: str,
                                    reward_batch_id: str,
                                    access_token: str):
    return post_validate_reward_batch(
        initiative_id,
        reward_batch_id,
        access_token
    )


def parse_transaction_names(trx_names: str) -> list[str]:
    normalized_names = trx_names.replace(" and ", ",")
    parsed_names = [name.strip() for name in normalized_names.split(",") if name.strip()]
    assert len(parsed_names) >= 2, (
        f'At least 2 transaction names are required, received: "{trx_names}"'
    )
    return parsed_names


def assert_transactions_share_same_reward_batch(trx_names: list[str],
                                                transaction_ids_by_name: dict[str, str],
                                                access_tokens_by_name: dict[str, str],
                                                merchant_id: str) -> str:
    eligibilities_by_trx = {}
    for trx_name in trx_names:
        eligibilities_by_trx[trx_name] = retry_reward_batch_eligibility(
            transaction_id=transaction_ids_by_name[trx_name],
            merchant_id=merchant_id,
            access_token=access_tokens_by_name[trx_name],
            expected_associated=True
        )

    first_trx_name = trx_names[0]
    first_reward_batch_id = eligibilities_by_trx[first_trx_name]["rewardBatchId"]
    for trx_name in trx_names[1:]:
        assert eligibilities_by_trx[trx_name]["rewardBatchId"] == first_reward_batch_id, (
            f"Transactions {first_trx_name} and {trx_name} are not in the same reward batch: "
            f'{first_reward_batch_id} vs {eligibilities_by_trx[trx_name]["rewardBatchId"]}'
        )

    return first_reward_batch_id


def _build_report_request(range_days: int, report_type: str) -> ReportRequest:
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=range_days - 1)

    start_period = datetime.datetime.combine(start_date, datetime.time.min)
    end_period = datetime.datetime.combine(
        end_date,
        datetime.time(23, 59, 59, 999000),
    )

    return ReportRequest(
        start_period=start_period,
        end_period=end_period,
        report_type=report_type,
    )

def _extract_report_request_id(response) -> str:
    payload = response.json()
    if isinstance(payload, dict):
        if payload.get('id') is not None:
            return payload['id']
        if payload.get('reportId') is not None:
            return payload['reportId']
        reports = payload.get('reports')
        if isinstance(reports, list) and reports and isinstance(reports[0], dict) and reports[0].get('id') is not None:
            return reports[0]['id']
    if isinstance(payload, list) and payload and isinstance(payload[0], dict) and payload[0].get('id') is not None:
        return payload[0]['id']
    raise AssertionError(f'Unable to extract report id from response: {response.text}')

def _find_report_in_list(report_list: list[dict], report_id: str) -> dict:
    for report in report_list:
        if report.get('id') == report_id:
            return report
    raise AssertionError(f'Report id {report_id} not found in report list: {report_list}')


def _extract_reports_payload(response) -> list[dict]:
    payload = response.json()
    if isinstance(payload, dict):
        reports = payload.get('reports')
        if isinstance(reports, list):
            return reports
        content = payload.get('content')
        if isinstance(content, list):
            return content
    if isinstance(payload, list):
        return payload
    raise AssertionError(f'Unable to extract reports list from response: {response.text}')
