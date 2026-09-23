"""CSV templates and unique product rows sent to the configured RDB environment."""
import csv
import io
import uuid

HEADERS = ['Codice GTIN/EAN', 'Codice Prodotto', 'Categoria',
           'Paese di Produzione', 'Marca', 'Modello']


def csv_bytes(headers, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=';', lineterminator='\n')
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def cooking_products(count=1):
    rows = []
    for _ in range(count):
        code = uuid.uuid4().hex[:14]
        rows.append([code, f'P{code}', 'Piano cottura', 'IT', 'RDB Test', f'M{code}'])
    return rows
