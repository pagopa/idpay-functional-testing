import time

from behave import given
from behave import then
from behave import when

from api.transaction import get_reports, get_report_download
from api.transaction import post_generate_report
from util.transaction_utilities import get_institution_selfcare_token, _build_report_request, \
    _extract_report_request_id, _find_report_in_list, _extract_reports_payload


@given('the operator with role {role} selects merchant {merchant_name} and a date range of {range_days} days')
def step_operator_selects_report_parameters(context, role, merchant_name, range_days):
    context.report_role = role
    context.report_merchant_name = merchant_name
    context.report_request = _build_report_request(
        range_days=int(range_days),
        report_type='MERCHANT_TRANSACTIONS',
    )
    context.report_merchant_id = context.merchants[merchant_name]['id']
    context.report_access_token = get_institution_selfcare_token(role)


@given('the operator with role {role} prepares report type {report_type} for merchant {merchant_name} with a date range of {range_days} days')
def step_operator_selects_report_parameters_with_type(context, role, merchant_name, report_type, range_days):
    context.report_role = role
    context.report_merchant_name = merchant_name
    context.report_request = _build_report_request(
        range_days=int(range_days),
        report_type=report_type,
    )
    context.report_merchant_id = context.merchants[merchant_name]['id']
    context.report_access_token = get_institution_selfcare_token(role)


@given('the operator with role {role} selects report type {report_type} and a date range of {range_days} days')
def step_operator_selects_report_parameters_without_merchant(context, role, report_type, range_days):
    context.report_role = role
    context.report_request = _build_report_request(
        range_days=int(range_days),
        report_type=report_type,
    )
    context.report_merchant_id = None
    context.report_access_token = get_institution_selfcare_token(role)


@given('the operator requests the CSV report export')
@when('the operator tries to request the CSV report export')
@then('the operator requests the CSV report export')
def step_operator_requests_csv_report_export(context):
    response = post_generate_report(
        initiative_id=context.initiative_id,
        request_body=context.report_request,
        merchant_id=context.report_merchant_id,
        access_token=context.report_access_token,
    )
    context.latest_report_response = response
    context.latest_report_request_id = None
    if response.status_code == 200:
        context.latest_report_request_id = _extract_report_request_id(response)

@given('the report request is inserted')
@then('the report request is inserted')
def step_report_request_is_inserted(context):
    generation_response = context.latest_report_response
    assert generation_response.status_code == 200, (
        f'Report generation failed: {generation_response.status_code} {generation_response.text}'
    )

    report_id = context.latest_report_request_id
    report = None
    for _ in range(10):
        reports_response = get_reports(
            initiative_id=context.initiative_id,
            report_type=context.report_request.report_type,
            access_token=context.report_access_token,
        )
        assert reports_response.status_code == 200, (
            f'Reports list failed: {reports_response.status_code} {reports_response.text}'
        )
        reports = _extract_reports_payload(reports_response)
        try:
            report = _find_report_in_list(reports, report_id)
            if report.get('reportStatus') == 'INSERTED':
                break
        except AssertionError:
            report = None
        time.sleep(3)

    assert report is not None, f'Report {report_id} not found in reports list'
    assert report.get('id') == report_id
    assert report.get('reportStatus') == 'INSERTED'


@then('the report request is rejected because the range exceeds 90 days')
def step_report_request_is_rejected(context):
    response = context.latest_report_response

    assert response.status_code == 400
    assert response.json()['code'] == 'INVALID_LENGTH_PERIOD'


@when('the operator tries to download the generated CSV report')
def step_operator_downloads_generated_csv_report(context):
    context.latest_report_download_response = retry_generated_report_download(
        context=context
    )

@then('the CSV report is downloaded correctly')
def step_csv_report_is_downloaded_correctly(context):
    response = context.latest_report_download_response
    assert response.status_code == 200, (
        f'Expected CSV report download to succeed, got {response.status_code} {response.text}'
    )
    assert response.content

def retry_generated_report_download(context, tries: int = 10, delay: int = 30):
    last_download_response = None
    last_report = None

    for attempt in range(tries):
        reports_response = get_reports(
            initiative_id=context.initiative_id,
            report_type=context.report_request.report_type,
            access_token=context.report_access_token,
        )
        assert reports_response.status_code == 200, (
            f'Reports list failed: {reports_response.status_code} {reports_response.text}'
        )

        last_report = _find_report_in_list(
            _extract_reports_payload(reports_response),
            context.latest_report_request_id,
        )

        download_response = get_report_download(
            initiative_id=context.initiative_id,
            report_id=context.latest_report_request_id,
            access_token=context.report_access_token,
        )
        last_download_response = download_response

        if download_response.status_code == 200 and download_response.content and last_report.get('reportStatus') == 'GENERATED':
            return download_response

        if attempt < tries - 1:
            time.sleep(delay)

    assert last_download_response is not None
    assert last_report is not None
    raise AssertionError(
        f'CSV report download failed for report {context.latest_report_request_id}. '
        f'Last report status: {last_report.get("reportStatus")}. '
    )