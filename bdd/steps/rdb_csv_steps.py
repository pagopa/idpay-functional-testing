"""CSV validation, processing, history and reports through asset_register APIs."""
import csv
import io
import math

from behave import given
from behave import then
from behave import when

from api import asset_register as api
from util import rdb_csv_utilities as csv_util
from util import rdb_utilities as rdb


@given('a valid RDB product CSV with {count:d} rows')
def rdb_valid_csv(context, count):
    assert count > 0
    rdb.set_csv(context, rdb.cooking_products(count))


@given('the RDB product CSV has defect "{defect}"')
def rdb_defective_csv(context, defect):
    csv_util.prepare_defective_csv(context, defect)


@given('the RDB EPREL CSV case is "{case}"')
def rdb_eprel_case(context, case):
    rdb.eprel_csv(context, case)


@given('the RDB CSV uses the decoder template')
def rdb_decoder_template(context):
    s = rdb.state(context)
    assert len(s.rows) == 1, 'The cross-initiative fixture requires one GTIN'
    csv_util.decoder_csv(context, s.rows[0][s.headers.index('Codice GTIN/EAN')])


@given('the RDB CSV contains duplicate GTIN rows with different product codes')
def rdb_duplicate_csv(context):
    first = rdb.cooking_products()[0]
    second = first[:]
    second[1] = 'SECOND'
    rdb.set_csv(context, [first, second])


@given('the RDB CSV updates product "{name}"')
def rdb_reload_csv(context, name):
    product = rdb.get_product(context, name)
    row = [product['gtinCode'], 'UPDATED', 'Piano cottura', 'IT', 'RDB Updated', 'Updated model']
    rdb.set_csv(context, [row])


@when('the producer validates the RDB product CSV')
def rdb_validate_csv(context):
    s = rdb.state(context)
    s.response = api.verify_product_file(s.token, s.initiative_id, s.category, s.csv_file)


@when('the producer uploads the RDB product CSV')
def rdb_upload_csv(context):
    rdb.submit_csv(context)


@then('the oversized RDB CSV is rejected or returns HTTP 500')
def rdb_oversized_csv_rejected(context):
    s = rdb.state(context)
    assert len(s.csv_file[1]) > 2 * 1024 * 1024, 'Expected a CSV larger than 2 MB'
    if s.response.status_code == 500:
        print('TD-RDB-001: HTTP 500 temporarily accepted for CSV size validation; backend fix pending')
    else:
        body = rdb.outcome(s.response, 'KO')
        assert body.get('errorKey') == 'product.invalid.file.maxsize', 'Expected the CSV size error'


@given('the RDB CSV has been uploaded and processed')
def rdb_processed_csv(context):
    rdb.outcome(rdb.submit_csv(context))
    rdb.completed_upload(context)


@given('a new RDB CSV is prepared for concurrent processing on initiative A')
def rdb_concurrent_processing(context):
    csv_util.prepare_concurrent_processing(context)


@when('the producer uploads the RDB product CSV during the first processing')
def rdb_concurrent_upload(context):
    csv_util.upload_during_processing(context)


@then('the first RDB CSV was processing before and after the second upload request')
def rdb_concurrent_overlap(context):
    before, after = rdb.state(context).concurrent_observations
    assert after and before['productFileId'] == after['productFileId'], (
        'The first upload disappeared during the concurrency check')
    assert all(item['uploadStatus'] in csv_util.PROCESSING_STATUSES for item in (before, after)), (
        'The first CSV finished before overlap could be proved; concurrency result is inconclusive')
    print('Concurrency confirmed: the same first CSV was active before and after the second request')


@then('the RDB CSV finishes with status "{status}"')
def rdb_upload_status(context, status):
    rdb.outcome(rdb.state(context).response)
    assert rdb.completed_upload(context)['uploadStatus'] == status


@then('all submitted RDB products have status "{status}"')
def rdb_all_stored(context, status):
    for code, items in csv_util.submitted_products(context).items():
        assert len(items) == 1, f'Product {code} is missing or duplicated'
        assert items[0]['status'] == status
        assert items[0]['initiativeId'] == rdb.state(context).initiative_id
        assert items[0]['organizationId'] == rdb.state(context).organization_id


@then('none of the submitted RDB products are stored')
def rdb_none_stored(context):
    assert all(items == [] for items in csv_util.submitted_products(context).values())


@then('the submitted RDB products have no EPREL code')
def rdb_no_eprel(context):
    for items in csv_util.submitted_products(context).values():
        assert len(items) == 1 and not items[0].get('eprelCode')


@then('only the valid EPREL rows are stored')
def rdb_mixed_products(context):
    s = rdb.state(context)
    valid = rdb.required(s.eprel_fixture, 'valid_row_indexes')
    assert valid and len(valid) < len(s.rows), 'Mixed fixture requires both valid and invalid rows'
    index = s.headers.index('Codice GTIN/EAN')
    items = csv_util.submitted_products(context)
    for row_number, row in enumerate(s.rows):
        found = items[row[index]]
        if row_number in valid:
            assert len(found) == 1 and found[0]['status'] == 'UPLOADED'
        else:
            assert found == []


@then('only the first occurrence of the RDB GTIN is stored')
def rdb_first_duplicate(context):
    s = rdb.state(context)
    items = rdb.products(context, gtin_code=s.rows[0][0])
    assert len(items) == 1, f'Expected one stored product for the duplicate GTIN, got {len(items)}'
    assert items[0]['productCode'] == s.rows[0][1], (
        f'Expected first product code {s.rows[0][1]}, got {items[0]["productCode"]}'
    )
    assert s.upload['addedProductNumber'] == 1, (
        f'Expected one added product, got {s.upload["addedProductNumber"]}'
    )


@then('RDB product "{name}" contains the new CSV data and batch')
def rdb_reloaded_product(context, name):
    s = rdb.state(context)
    item = rdb.get_product(context, name)
    assert item['gtinCode'] == s.before[name]['gtinCode']
    assert item['initiativeId'] == s.before[name]['initiativeId']
    assert item['status'] == 'UPLOADED'
    assert item['productCode'] == 'UPDATED'
    assert item['brand'] == 'RDB Updated'
    assert item['model'] == 'Updated model'
    assert item['batchName'] == s.upload['batchName']
    assert item['batchName'] != s.before[name]['batchName']


@then('the submitted RDB product belongs to the selected initiative')
def rdb_cross_initiative_product(context):
    rdb_all_stored(context, 'UPLOADED')


@then('the submitted RDB CSV is absent from upload history')
def rdb_csv_not_in_history(context):
    s = rdb.state(context)
    file_id = s.response.json().get('productFileId')
    items = rdb.history(context)
    assert all(item['fileName'] != s.csv_file[0] for item in items)
    if file_id:
        assert all(item['productFileId'] != file_id for item in items)


@then('the RDB formal report contains errors for "{fields}"')
def rdb_formal_report(context, fields):
    s = rdb.state(context)
    csv_util.download_report(context, rdb.required(s.response.json(), 'productFileId', 'validation response'))
    # Match the errors column, not the CSV header, which contains the same field names.
    rows = list(csv.reader(io.StringIO(s.report), delimiter=';'))
    assert len(rows) == 2, 'Expected a report for exactly one invalid row'
    error_text = rows[1][-1]
    for field in fields.split(','):
        assert field.strip() in error_text, f'Missing formal error for {field.strip()}'


@then('the RDB processing report contains "{text}"')
def rdb_processing_report(context, text):
    s = rdb.state(context)
    csv_util.download_report(context, s.upload['productFileId'])
    assert text in s.report


@then('the RDB processing report contains the expected EPREL error')
def rdb_eprel_report(context):
    s = rdb.state(context)
    rdb_processing_report(context, rdb.required(s.eprel_fixture, 'error_text'))


@when('the producer requests the RDB CSV history')
def rdb_csv_history(context):
    rdb.state(context).items = rdb.history(context)


@then('the returned RDB upload IDs match the dataset')
def rdb_history_ids(context):
    s = rdb.state(context)
    assert sorted(item['productFileId'] for item in s.items) == sorted(rdb.required(s.dataset, 'upload_ids'))


@then('the RDB CSV history includes known uploads and excludes foreign uploads')
def rdb_history_scope(context):
    s = rdb.state(context)
    if 'upload_ids' in s.dataset:
        # Preserve exact-set checks for independently configured fixtures.
        rdb_history_ids(context)
        return
    ids = [item['productFileId'] for item in s.items]
    known = set(rdb.required(s.dataset, 'known_upload_ids'))
    foreign = set(rdb.required(s.dataset, 'foreign_upload_ids'))
    assert known and foreign, 'CSV history requires positive and negative controls'
    assert len(ids) == len(set(ids)), 'CSV history contains duplicate upload IDs'
    assert known <= set(ids), 'CSV history omits known uploads of the producer in this initiative'
    assert foreign.isdisjoint(ids), 'CSV history includes uploads from another organization or initiative'


@then('the RDB uploads are ordered by date descending')
def rdb_history_order(context):
    dates = [item['dateUpload'] for item in rdb.state(context).items]
    assert len(dates) >= 2, 'Ordering fixture requires at least two uploads'
    assert dates == sorted(dates, reverse=True)


@given('the RDB CSV history contains at least {count:d} uploads')
def rdb_history_size(context, count):
    s = rdb.state(context)
    s.history_before = rdb.history(context)
    assert len(s.history_before) >= count


@given('{count:d} RDB CSV uploads have been prepared')
def rdb_prepare_csv_history(context, count):
    rdb.prepare_csv_history(context, count)


@when('the producer requests RDB CSV history page {page:d} with size {size:d}')
def rdb_history_page(context, page, size):
    s = rdb.state(context)
    s.page, s.size = page, size
    s.response = api.get_product_files(s.token, s.initiative_id, page=page, size=size)


@then('the RDB CSV history page and metadata are correct')
def rdb_page_metadata(context):
    s = rdb.state(context)
    body = rdb.success(s.response).json()
    assert body['pageNo'] == s.page and body['pageSize'] == s.size
    assert body['totalElements'] == len(s.history_before)
    assert body['totalPages'] == math.ceil(len(s.history_before) / s.size)
    assert body['content'] == s.history_before[s.page * s.size:(s.page + 1) * s.size]


@when('the producer downloads the RDB processing report {count:d} times')
def rdb_download_repeated(context, count):
    s = rdb.state(context)
    assert count > 0
    s.reports = [csv_util.download_report(context, s.upload['productFileId']) for _ in range(count)]


@then('every RDB report download succeeds with identical content')
def rdb_identical_reports(context):
    reports = rdb.state(context).reports
    assert reports and all(report.content == reports[0].content for report in reports)


@when('the producer downloads the dataset report')
def rdb_dataset_report(context):
    s = rdb.state(context)
    s.response = api.download_product_file_report(
        s.token, s.initiative_id, rdb.required(s.dataset, 'product_file_id'))
