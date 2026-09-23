"""Prepare CSV cases and retrieve their products and reports through real RDB APIs."""
import json
import uuid

from api import asset_register as api
from util import rdb_utilities as rdb


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
