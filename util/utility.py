import csv
import datetime
import time


from api.idpay import delete_initiative
from api.idpay import delete_transaction_bar_code_merchant
from api.idpay import get_initiative_statistics
from api.idpay import get_reward_batch_eligibility
from api.idpay import obtain_merchant_test_token
from api.idpay import obtain_selfcare_test_token
from api.idpay import post_initiative_info
from api.idpay import publish_approved_initiative
from api.idpay import put_initiative_approval
from api.idpay import put_initiative_beneficiary_info
from api.idpay import put_initiative_general_info
from api.idpay import put_initiative_refund_info
from api.idpay import put_initiative_reward_info
from api.idpay import timeline
from api.idpay import unsubscribe
from api.idpay import upload_whitelist_csv
from api.idpay import wallet
from conf.configuration import secrets
from conf.configuration import settings
from util.dataset_utility import euros_to_cents
from util.onboarding_utilities import get_io_token

PAYMENT_OK = 'OK - ORDINE ESEGUITO'
PAYMENT_KO = 'KO'
REJECT_REASON = 'IBAN NOT VALID'
reward_columns = [
    'uniqueID',
    'result',
    'rejectionReason',
    'cro',
    'executionDate'
]

timeline_operations = settings.IDPAY.endpoints.timeline.operations
wallet_statuses = settings.IDPAY.endpoints.wallet.statuses


def get_selfcare_token(institution_info: str):
    """Login through Self Care mock
    :param institution_info: Information of the institute to log in.
    """
    return obtain_selfcare_test_token(institution_info).content.decode('utf-8')


def get_merchant_access_token(initiative_name: str, merchant_name: str):
    merchant = secrets.merchants[f'merchant_{merchant_name}']
    response = obtain_merchant_test_token({
        'aud': 'idpay.merchant.welfare.pagopa.it',
        'iss': settings.IDPAY.merchant_test_token_issuer,
        'uid': merchant['id'],
        'name': 'esercente',
        'familyName': 'test',
        'email': 'esercente_test@test.email.it',
        'acquirerId': settings.idpay.acquirer_id,
        'merchantId': merchant['id'],
        'orgId': secrets.initiatives[initiative_name]["organization_id"],
        'orgVAT': merchant['fiscal_code'],
        'orgName': 'Esercente di test IdPay',
        'orgPartyRole': 'MANAGER',
        'orgRole': 'admin',
        'pointOfSaleId': '1234'
    })
    assert response.status_code == 200, (
        f'Merchant test token failed: {response.status_code} {response.text}'
    )
    access_token = response.text
    assert access_token
    return access_token


def retry_timeline(expected, request, token, initiative_id, field, num_required=1, tries=3, delay=5,
                   message='Test failed', page: int = 0):
    count = 0
    res = request(initiative_id, token, page)

    if res.status_code == 404:
        res = request(initiative_id, token, page)
        while res.status_code == 404:
            time.sleep(delay)
            res = request(initiative_id, token, page)

    operations = []
    for operation in res.json()['operationList']:
        if field in operation:
            if operation[field] == expected:
                operations.append(operation)
    success = len(operations) == num_required

    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(initiative_id, token, page)

        operations = []
        for operation in res.json()['operationList']:
            if field in operation:
                if operation[field] == expected:
                    operations.append(operation)
        success = len(operations) == num_required

    assert success, (
        f'result retry timeline {res.json()[field]} does not match expected {expected} for field {field}')
    return res


def retry_wallet(expected, request, token, initiative_id, field, tries=3, delay=5):
    count = 0
    res = request(initiative_id, token)
    success = (res.status_code == 200 and expected == res.json()[field])
    while not success:
        count += 1
        if count == tries:
            break
        time.sleep(delay)
        res = request(initiative_id, token)
        success = (res.status_code == 200 and expected == res.json()[field])
    assert success, (
        f'result retry wallet {res.json()[field]} does not match expected {expected} for field {field}'
    )
    return res


def retry_bar_code_transaction_cancellation(initiative_id: str,
                                            transaction_id: str,
                                            access_token: str,
                                            tries: int = 5,
                                            delay: int = 1):
    response = delete_transaction_bar_code_merchant(
        initiative_id=initiative_id,
        transaction_id=transaction_id,
        access_token=access_token
    )
    count = 0

    while (
        response.status_code == 429
        and response.json().get('code') == 'PAYMENT_TRANSACTION_VERSION_PENDING'
        and count < tries
    ):
        count += 1
        time.sleep(delay)
        response = delete_transaction_bar_code_merchant(
            initiative_id=initiative_id,
            transaction_id=transaction_id,
            access_token=access_token
        )

    return response


def expect_wallet_counters(expected_amount: float, expected_accrued: float, token: str, initiative_id: str,
                           tries: int = 10, delay: int = 5):
    retry_wallet(expected=euros_to_cents(expected_amount), request=wallet, token=token,
                 initiative_id=initiative_id, field='amountCents', tries=tries, delay=delay)

    retry_wallet(expected=euros_to_cents(expected_accrued), request=wallet, token=token,
                 initiative_id=initiative_id, field='accruedCents', tries=tries, delay=delay)


def retry_institution_statistics(initiative_id: str,
                                 organization_id: str = None,
                                 tries=10,
                                 delay=1):
    if organization_id is None:
        organization_id = secrets.organization_id
    count = 0

    res = get_initiative_statistics(
        organization_id=organization_id,
        initiative_id=initiative_id)

    while res.status_code != 200:
        count += 1
        time.sleep(delay)
        res = get_initiative_statistics(
            organization_id=organization_id,
            initiative_id=initiative_id)
        if count == tries:
            break

    assert res.status_code == 200, (
        f'get_initiative_statistics failed: status={res.status_code}, body={res.text}'
    )
    return res.json()


def retry_publishing_initiative(selfcare_token: str,
                                initiative_id: str,
                                tries=10,
                                delay=3):
    count = 0
    res = publish_approved_initiative(selfcare_token=selfcare_token,
                                      initiative_id=initiative_id)

    while res.status_code != 204:
        count += 1
        time.sleep(delay)
        res = publish_approved_initiative(selfcare_token=selfcare_token,
                                          initiative_id=initiative_id)
        if count == tries:
            break

    assert res.status_code == 204


def check_statistics(organization_id: str,
                     initiative_id: str,
                     old_statistics: dict,
                     onboarded_citizen_count_increment: int,
                     accrued_rewards_increment: float,
                     rewarded_trxs_increment: int = 1,
                     skip_trx_check: bool = False,
                     tries=62,
                     delay=5,
                     deadline=None):
    success = False
    count = 0
    current_statistics = None

    while not success:
        if deadline is not None and count > 0 and time.monotonic() >= deadline:
            break

        current_statistics = get_initiative_statistics(organization_id=organization_id,
                                                       initiative_id=initiative_id).json()
        are_onboards_incremented = (current_statistics['onboardedCitizenCount'] == old_statistics[
            'onboardedCitizenCount'] + onboarded_citizen_count_increment)

        are_accrued_rewards_incremented = (round(current_statistics['accruedRewards'], 2) ==
                                           round(old_statistics['accruedRewards'] + accrued_rewards_increment, 2))

        if not skip_trx_check:
            are_trxs_incremented = (
                    current_statistics['rewardedTrxs'] == old_statistics['rewardedTrxs'] + rewarded_trxs_increment)
        else:
            are_trxs_incremented = True

        success = are_onboards_incremented and are_accrued_rewards_incremented and are_trxs_incremented
        if success:
            break

        count += 1
        if deadline is None and count == tries:
            break
        sleep_duration = delay
        if deadline is not None:
            remaining_time = deadline - time.monotonic()
            if remaining_time <= 0:
                break
            sleep_duration = min(delay, remaining_time)
        time.sleep(sleep_duration)

    assert success, (f'Initiative statistics did not reach the expected values: {current_statistics}. '
                     f'Previous: {old_statistics}, expected increments: onboarded={onboarded_citizen_count_increment}, '
                     f'rewardedTrxs={rewarded_trxs_increment} (skipped={skip_trx_check}), '
                     f'accruedRewards={accrued_rewards_increment}')


def retry_reward_batch_eligibility(transaction_id: str,
                                   merchant_id: str,
                                   access_token: str,
                                   expected_associated: bool,
                                   tries: int = 20,
                                   delay: int = 3):
    latest_response = None
    for attempt in range(tries):
        latest_response = get_reward_batch_eligibility(
            transaction_id=transaction_id,
            merchant_id=merchant_id,
            access_token=access_token
        )
        assert latest_response.status_code in {200, 204}, (
            f'Reward batch eligibility request failed: '
            f'{latest_response.status_code} {latest_response.text}'
        )
        associated = latest_response.status_code == 200
        if associated == expected_associated:
            return latest_response.json() if associated else None

        if attempt < tries - 1:
            time.sleep(delay)

    assert False, (
        f'Transaction {transaction_id} eligibility association did not become '
        f'{expected_associated}. Last response: '
        f'{latest_response.status_code} {latest_response.text}'
    )


def retry_reward_batch_reassignment(transaction_id: str,
                                    merchant_id: str,
                                    access_token: str,
                                    original_reward_batch_id: str,
                                    expected_batch_transaction_status: str = 'SUSPENDED',
                                    tries: int = 20,
                                    delay: int = 3):
    latest_eligibility = None
    for attempt in range(tries):
        response = get_reward_batch_eligibility(
            transaction_id=transaction_id,
            merchant_id=merchant_id,
            access_token=access_token
        )
        assert response.status_code == 200, (
            f'Reward batch eligibility request failed while waiting for reassignment: '
            f'{response.status_code} {response.text}'
        )
        latest_eligibility = response.json()

        if latest_eligibility['rewardBatchId'] != original_reward_batch_id:
            assert latest_eligibility['transactionStatus'] == 'INVOICED', (
                f'Invoice replacement impact moved transaction {transaction_id}, but left '
                f'transactionStatus={latest_eligibility["transactionStatus"]}'
            )
            assert latest_eligibility['batchTransactionStatus'] == expected_batch_transaction_status, (
                f'Invoice replacement impact moved transaction {transaction_id}, but left '
                f'batchTransactionStatus={latest_eligibility["batchTransactionStatus"]}'
            )
            return latest_eligibility

        if attempt < tries - 1:
            time.sleep(delay)

    assert False, (
        f'Invoice replacement impact was not observed for transaction {transaction_id}. '
        f'The transaction remained in reward batch {original_reward_batch_id}. '
        f'Last eligibility: {latest_eligibility}'
    )


def natural_language_to_date_converter(natural_language_date: str):
    if natural_language_date == 'today':
        actual_date = datetime.datetime.now().strftime('%Y-%m-%d')
    elif natural_language_date == 'tomorrow':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    elif natural_language_date == 'ten_days_from_tomorrow':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=12)).strftime('%Y-%m-%d')
    elif natural_language_date == 'day_after_tomorrow':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    elif natural_language_date == 'future':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=365 * 5)).strftime('%Y-%m-%d')
    elif natural_language_date == 'future_tomorrow':
        actual_date = (datetime.datetime.now() + datetime.timedelta(days=365 * 5 + 1)).strftime('%Y-%m-%d')
    else:
        actual_date = datetime.datetime.strptime(natural_language_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    return actual_date


def create_initiative(initiative_name_in_settings: str,
                      known_beneficiaries: list = None):
    creation_payloads = settings.initiatives[initiative_name_in_settings].creation_payloads

    institution_selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)
    initiative_id = post_initiative_info(selfcare_token=institution_selfcare_token).json()['initiativeId']

    if 'rankingStartDate' in creation_payloads.general:
        creation_payloads.general['rankingStartDate'] = natural_language_to_date_converter(
            creation_payloads.general['rankingStartDate'])
    if 'rankingEndDate' in creation_payloads.general:
        creation_payloads.general['rankingEndDate'] = natural_language_to_date_converter(
            creation_payloads.general['rankingEndDate'])

    creation_payloads.general['startDate'] = natural_language_to_date_converter(creation_payloads.general['startDate'])
    creation_payloads.general['endDate'] = natural_language_to_date_converter(creation_payloads.general['endDate'])

    res = put_initiative_general_info(selfcare_token=institution_selfcare_token,
                                      initiative_id=initiative_id,
                                      general_payload=creation_payloads.general)
    assert res.status_code == 204, (
        f'put_initiative_general_info failed for initiative "{initiative_name_in_settings}" '
        f'(id={initiative_id}): status={res.status_code}, body={res.text}'
    )

    if creation_payloads.general['beneficiaryKnown'] is True:
        res = upload_whitelist_file(selfcare_token=institution_selfcare_token,
                                    initiative_id=initiative_id,
                                    fiscal_codes=known_beneficiaries)
        assert res.status_code == 200, (
            f'upload_whitelist_file failed for initiative "{initiative_name_in_settings}" '
            f'(id={initiative_id}): status={res.status_code}, body={res.text}'
        )
        time.sleep(5)
    else:
        res = put_initiative_beneficiary_info(selfcare_token=institution_selfcare_token,
                                              initiative_id=initiative_id,
                                              beneficiary_payload=creation_payloads.beneficiary)
        assert res.status_code == 204, (
            f'put_initiative_beneficiary_info failed for initiative "{initiative_name_in_settings}" '
            f'(id={initiative_id}): status={res.status_code}, body={res.text}'
        )

    res = put_initiative_reward_info(selfcare_token=institution_selfcare_token,
                                     initiative_id=initiative_id,
                                     reward_payload=creation_payloads.reward
                                     )
    assert res.status_code == 204, (
        f'put_initiative_reward_info failed for initiative "{initiative_name_in_settings}" '
        f'(id={initiative_id}): status={res.status_code}, body={res.text}'
    )

    res = put_initiative_refund_info(selfcare_token=institution_selfcare_token,
                                     initiative_id=initiative_id,
                                     refund_payload=creation_payloads.refund
                                     )
    assert res.status_code == 204, (
        f'put_initiative_refund_info failed for initiative "{initiative_name_in_settings}" '
        f'(id={initiative_id}): status={res.status_code}, body={res.text}'
    )

    pagopa_selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.PagoPA)
    res = put_initiative_approval(selfcare_token=pagopa_selfcare_token,
                                  initiative_id=initiative_id)
    assert res.status_code == 204, (
        f'put_initiative_approval failed for initiative "{initiative_name_in_settings}" '
        f'(id={initiative_id}): status={res.status_code}, body={res.text}'
    )

    institution_selfcare_token = get_selfcare_token(institution_info=secrets.selfcare_info.test_institution)

    retry_publishing_initiative(selfcare_token=institution_selfcare_token, initiative_id=initiative_id)

    return initiative_id


def create_initiative_and_update_conf(initiative_name: str,
                                      known_beneficiaries: list = None):
    secrets['initiatives'][initiative_name]['id'] = create_initiative(initiative_name_in_settings=initiative_name,
                                                                   known_beneficiaries=known_beneficiaries)
    secrets["initiatives"][initiative_name]["organization_id"] = secrets.selfcare_info.test_institution["orgId"]
    print(f'Created initiative for {initiative_name}')
    secrets['newly_created'].add(secrets['initiatives'][initiative_name]['id'])

    startup_time = settings.INITIATIVE_STARTUP_TIME_SECONDS
    if 'initiative_startup_time_seconds' in settings.initiatives[initiative_name]:
        startup_time = settings.initiatives[initiative_name]['initiative_startup_time_seconds']
    time.sleep(startup_time)


def delete_new_initiatives_after_test():
    if not settings.KEEP_INITIATIVES_AFTER_TEST:
        for initiative_id in secrets['newly_created']:
            res = delete_initiative(initiative_id=initiative_id, domain="/idpay")
            if res.status_code == 204:
                print(f'Deleted initiative {initiative_id}')
            else:
                print(f'Failed to delete initiative {initiative_id}, {res.status_code}, {res.text}')


def upload_whitelist_file(selfcare_token: str,
                          initiative_id: str,
                          fiscal_codes: list):
    csv_file_path = f'fiscal_codes_{datetime.datetime.now().strftime("%Y%m%d.%H%M%S")}.csv'

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for fc in fiscal_codes:
            writer.writerow([fc])

    whitelist_csv_upload_payload = {'file': (csv_file_path, open(csv_file_path, 'rb'), 'text/csv')}

    return upload_whitelist_csv(selfcare_token=selfcare_token,
                                initiative_id=initiative_id,
                                whitelist_payload=whitelist_csv_upload_payload
                                )


def citizen_unsubscribe_from_initiative(initiative_id: str,
                                        fiscal_code: str):
    token = get_io_token(fiscal_code)
    res = unsubscribe(initiative_id, token)
    assert res.status_code == 204
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    retry_wallet(expected=wallet_statuses.unsubscribed, request=wallet, token=token,
                 initiative_id=initiative_id, field='status', tries=3, delay=3)
    retry_timeline(expected=timeline_operations.unsubscribed, request=timeline, num_required=1, token=token,
                   initiative_id=initiative_id, field='operationType', tries=10, delay=3,
                   message='Not unsubscribed')
