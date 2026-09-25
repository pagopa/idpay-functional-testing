"""Prepare CSV cases and retrieve their products and reports through real RDB APIs."""
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from api import asset_register as api
from util import rdb_utilities as rdb


PROCESSING_STATUSES = ('UPLOADED', 'IN_PROCESS')
FINISHED_STATUSES = ('LOADED', 'PARTIAL')


def processing_upload(fixture):
    # Only two files can be added by this sequential scenario. Reading the
    # newest page avoids losing the overlap while paging through old uploads.
    items = rdb.success(api.get_product_files(
        fixture['token'], fixture['initiative_id'], page=0, size=10)).json()['content']
    matches = [item for item in items if item['fileName'] == fixture['filename']]
    assert len(matches) <= 1, 'The concurrency CSV appears more than once in history'
    return matches[0] if matches else None


def prepare_concurrent_processing(context):
    """Prepare a scenario-owned CSV using the configured test producer on A/B."""
    rdb.authenticate(context, 'producer')
    s = rdb.state(context)
    enabled = {item['initiativeId'] for item in rdb.success(api.get_initiatives(s.token)).json()
               if item['enabled']}
    initiatives = {rdb.select_initiative(context, alias) for alias in ('A', 'B')}
    assert len(initiatives) == 2 and initiatives <= enabled, (
        'Concurrency requires the configured test producer enabled on distinct initiatives A/B')
    for alias in ('A', 'B'):
        rdb.select_initiative(context, alias)
        assert all(item['uploadStatus'] not in PROCESSING_STATUSES for item in rdb.history(context)), (
            f'Another CSV is already processing in {alias}; use a dedicated test producer')
    rdb.select_initiative(context, 'A')
    rdb.eprel_csv(context, 'valid')
    # The backend checks each row sequentially against EPREL. A normal batch
    # provides an overlap window without pausing or mocking any shared service.
    rows = []
    gtin_index = s.headers.index('Codice GTIN/EAN')
    for _ in range(100):
        row = s.rows[0][:]
        row[gtin_index] = uuid.uuid4().hex[:14]
        rows.append(row)
    rdb.set_csv(context, rows, s.headers, s.category)
    s.concurrent_upload = {'token': s.token, 'initiative_id': s.initiative_id,
                           'filename': s.csv_file[0], 'csv_file': s.csv_file,
                           'category': s.category}


def upload_during_processing(context):
    """Bracket the second request with observations of the first active upload."""
    s = rdb.state(context)
    fixture = s.concurrent_upload
    # Observe processing even if the first upload HTTP request has not returned.
    # The worker uses immutable arguments and never mutates the Behave context.
    with ThreadPoolExecutor(max_workers=1) as executor:
        first = executor.submit(api.upload_product_file, fixture['token'],
                                fixture['initiative_id'], fixture['category'], fixture['csv_file'])

        def observe():
            if first.done():
                rdb.outcome(first.result())
            item = processing_upload(fixture)
            assert not item or item['uploadStatus'] not in FINISHED_STATUSES, (
                'Concurrency precondition not observed: the first CSV already finished; '
                'the overlap has not been tested')
            return item

        def finish_first_upload():
            rdb.outcome(first.result())
            # Drain only this scenario's CSV, including on assertion failure.
            rdb.wait_for(lambda: processing_upload(fixture),
                         lambda item: item and item['uploadStatus'] in FINISHED_STATUSES,
                         'the scenario concurrency CSV to finish processing')

        try:
            before = rdb.wait_for(
                observe, lambda item: item and item['uploadStatus'] in PROCESSING_STATUSES,
                'the scenario CSV to enter processing', poll_interval=0.2)
            rdb.submit_csv(context)
            after = processing_upload(fixture)
            s.concurrent_observations = (before, after)
        except Exception as error:
            try:
                finish_first_upload()
            except Exception as finish_error:
                error.add_note(f'Waiting for the first CSV also failed ({type(finish_error).__name__})')
            raise
        else:
            finish_first_upload()


def prepare_defective_csv(context, defect):
    rdb.set_csv(context)
    s = rdb.state(context)
    name, content, mime = s.csv_file
    if defect == 'not a CSV file':
        name = name.replace('.csv', '.txt')
        mime = 'text/plain'
    elif defect == 'empty':
        content = b''
    elif defect == 'header only':
        content = rdb.csv_bytes(s.headers, [])
    elif defect == 'larger than 2 MB':
        content += b'a' * (2 * 1024 * 1024 + 1)
    elif defect == 'more than 100 rows':
        s.rows = rdb.cooking_products(101)
        content = rdb.csv_bytes(s.headers, s.rows)
    elif defect == 'missing headers':
        content = rdb.csv_bytes(s.headers[1:], [row[1:] for row in s.rows])
    elif defect == 'additional headers':
        content = rdb.csv_bytes(s.headers + ['Extra'], [row + ['extra'] for row in s.rows])
    elif defect == 'headers in wrong order':
        content = rdb.csv_bytes(list(reversed(s.headers)), [list(reversed(row)) for row in s.rows])
    elif defect == 'unsupported category':
        s.category = 'UNSUPPORTED'
    elif defect == 'mismatching category':
        s.rows[0][2] = 'Lavatrice'
        content = rdb.csv_bytes(s.headers, s.rows)
    elif defect == 'multiple row errors':
        s.rows[0][0], s.rows[0][4], s.rows[0][5] = '', '', ''
        content = rdb.csv_bytes(s.headers, s.rows)
    else:
        raise ValueError(f'Unknown CSV defect: {defect}')
    s.csv_file = name, content, mime


def decoder_csv(context, gtin=None):
    # Backend postman/file/valid/terrestre_ok.csv, with a fresh business key.
    code = gtin or uuid.uuid4().hex[:14]
    return rdb.set_csv(context, [[code, 'TR01', 'DT', 'RDB Decoder', 'RDB Model']],
                       ['Codice GTIN/EAN', 'Codice Prodotto', 'Categoria', 'Marca', 'Modello'], 'DT')


def submitted_products(context):
    s = rdb.state(context)
    index = s.headers.index('Codice GTIN/EAN')
    result = {}
    for code in dict.fromkeys(row[index] for row in s.rows):
        assert code, 'Cannot look up a product with an empty GTIN'
        result[code] = rdb.products(context, gtin_code=code)
    return result


def download_report(context, file_id):
    s = rdb.state(context)
    response = rdb.success(api.download_product_file_report(s.token, s.initiative_id, file_id))
    assert response.content, 'The report is empty'
    assert 'attachment' in response.headers.get('Content-Disposition', '').lower()
    s.report = response.content.decode('utf-8-sig')
    # APIM wraps the CSV in {"data": "..."}; direct backend downloads return CSV.
    if s.report.lstrip().startswith('{'):
        body = json.loads(s.report)
        assert isinstance(body.get('data'), str), 'The JSON report must contain CSV text in data'
        s.report = body['data'].lstrip('\ufeff')
    assert s.report.strip(), 'The CSV report is empty'
    return response
