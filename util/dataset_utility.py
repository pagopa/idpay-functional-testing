import datetime
import os
import random
import uuid
from dataclasses import dataclass
from hashlib import sha256

import math
import pandas as pd
import pytz
from faker import Faker
from schwifty import IBAN
from six import unichr

from api.rtd import pm_salt

CSV_SEPARATOR = ';'

fake = Faker('it_IT')

circuits = ['visa', 'mastercard', 'maestro', 'amex']


@dataclass()
class reward:
    iban: str
    amount: float


@dataclass()
class merchantInfo:
    vat: str
    fc: str
    iban: str


def hash_pan(pan: str):
    """Function that hashes a PAN with salt got from the Payment Manager
    :param pan: Clear PAN to be encrypted.
    :returns:  The hashed  PAN.
    :rtype: str
    """
    salt = pm_salt()
    return sha256(f'{pan}{salt}'.encode()).hexdigest()


def fake_fc(age: int = None, custom_month: int = None, custom_day: int = None, sex: str = None):
    """Faker wrapper that generates a fake fiscal code with customizable parameters.
    :param age: Age of the fake fiscal code.
    :param custom_month: Custom month for the fiscal code (1-12).
    :param custom_day: Custom day for the fiscal code (1-31).
    :param sex: Sex of the person ('M' or 'F').
    :returns: A fake fiscal code.
    :rtype: str
    """
    fake_cf = fake.ssn()

    surname = fake_cf[:3]
    name = fake_cf[3:6]
    year = fake_cf[6:8]
    checksum = fake_cf[15]

    if age is not None:
        custom_year = (datetime.datetime.now() - datetime.timedelta(days=int(age) * 365))
        if custom_month is not None and custom_day is not None:
            valid_date = False
            while not valid_date:  # in case the day is Feb 29 and is not a leap year
                try:
                    datetime.datetime(custom_year.year, custom_month, custom_day)
                    valid_date = True
                except ValueError:
                    custom_day = custom_day - 1

        year = custom_year.strftime('%Y')[2:]

    if custom_month is not None and 1 <= custom_month <= 12:
        month_letter = month_number_to_fc_letter(custom_month)
    else:
        month_letter = fake_cf[8]

    if custom_day is not None and 1 <= custom_day <= 31:
        day = str(custom_day).zfill(2)
        if sex == 'F':
            day = int(day) + 40
        else:
            if int(day) > 31:
                day = str(int(day) - 40).zfill(2)
    else:
        day = fake_cf[9:11]

    return f'{surname}{name}{year}{month_letter}{day}X000{checksum}'


def fake_temporary_fc():
    """Utility to get a temporary fiscal code.
    :returns:  A temporary fiscal code.
    :rtype: str
    """
    return str(random.randint(0, 9999999999)).zfill(11)


def fake_pan():
    """Faker wrapper that calls faker's credit_card_number method and random circuit.
    :returns:  A fake PAN.
    :rtype: str
    """
    return fake.credit_card_number(random.choice(circuits))


def fake_iban(abi):
    """Wrapper that calls schwifty's IBAN method with arbitrary ABI code.
    :returns:  A fake IBAN.
    :rtype: str
    """
    curr_iban = IBAN.generate('IT', bank_code=abi,
                              account_code=str(round(random.random() * math.pow(10, 10))) + '99').compact
    return curr_iban[:len(curr_iban) - 2] + '99'


def fake_vat():
    """Faker wrapper that calls faker's vat method.
    :returns: a fake VAT.
    :rtype: str
    """
    return fake.company_vat()[2:]


def get_random_unicode(length):
    try:
        get_char = unichr
    except NameError:
        get_char = chr

    include_ranges = [
        (0x0021, 0x0021),
        (0x0023, 0x0026),
        (0x0028, 0x007E),
        (0x00A1, 0x00AC),
        (0x00AE, 0x00FF),
        (0x0100, 0x017F),
        (0x0180, 0x024F),
        (0x2C60, 0x2C7F),
        (0x16A0, 0x16F0),
        (0x0370, 0x0377),
        (0x037A, 0x037E),
        (0x0384, 0x038A),
        (0x038C, 0x038C),
    ]

    alphabet = [
        get_char(code_point) for current_range in include_ranges
        for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))


def get_random_time(start_time: str, end_time: str):
    """ Pick a random second between start_hour and end_time.
    :param start_time: Lower bound time formatted in hh:mm:ss.
    :param end_time: Upper bound time formatted in hh:mm:ss.
    :returns: A random timestamp formatted in hh:mm:ss.
    """
    curr_timestamp = random.randint(get_seconds(start_time), get_seconds(end_time))

    # "{:0>8}".format(MY_VAR) left-pads a string with '0' until it is 8 char long
    return '{:0>8}'.format(str(datetime.timedelta(seconds=curr_timestamp)))


def get_seconds(time_str: str):
    """ Convert timestamp in second span,
    :param time_str: Time formatted hh:mm:ss.
    :returns: The number of seconds, starting from 00:00:00, corresponding to the given time formatted in hh:mm:ss.
    """
    hh, mm, ss = time_str.split(':')
    return int(hh) * 3600 + int(mm) * 60 + int(ss)


def tomorrow_date(is_iso: bool = False):
    tomorrow_date_format = '%Y-%m-%d'
    if is_iso:
        tomorrow_date_format = tomorrow_date_format + 'T%H:%M:%S.000%z'
    return (datetime.datetime.now(pytz.timezone('Europe/Rome')) + datetime.timedelta(days=1)).strftime(
        tomorrow_date_format)


def yesterday_date(is_iso: bool = False):
    tomorrow_date_format = '%Y-%m-%d'
    if is_iso:
        tomorrow_date_format = tomorrow_date_format + 'T%H:%M:%S.000%z'
    return (datetime.datetime.now(pytz.timezone('Europe/Rome')) - datetime.timedelta(days=1)).strftime(
        tomorrow_date_format)


def month_number_to_fc_letter(month_num):
    months = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M', 'P', 'R', 'S', 'T']
    if 1 <= int(month_num) <= 12:
        return months[int(month_num) - 1]
    else:
        return 'A'


def serialize(dataset, columns, destination_path, have_header=False):
    dataset_dataframe = pd.DataFrame(dataset, columns=columns)
    trx_file_path = os.path.join(destination_path, )
    os.makedirs(os.path.dirname(trx_file_path), exist_ok=True)

    with open(trx_file_path, 'a', newline='') as f:
        f.write(dataset_dataframe.to_csv(index=False, header=have_header, sep=CSV_SEPARATOR, lineterminator='\n'))


def fake_merchant_file(acquirer_id: str,
                       merchants_info: [merchantInfo]):
    header = f'Acquirer ID;Ragione Sociale;Indirizzo sede legale;Comune sede legale;Provincia sede legale;CAP sede Legale;PEC;CF;PIVA;Nome Legale Rappresentante;Cognome Legale Rappresentante;CF Legale Rappresentante;Email Aziendale Legale rappresentante;Nome Amministratore;Cognome Amministratore;CF Amministratore;Email Aziendale Amministratore;IBAN'
    merchants_csv = [header]
    for merchant_info in merchants_info:
        merchants_csv.append(
            f'{acquirer_id};Esercente di test {datetime.datetime.now().strftime("%Y%m%d - %H%M%S")} {str(uuid.uuid4())[:4]};Indirizzo sede legale;Comune sede legale;Provincia sede legale;CAP sede Legale;email1@prova.it;{merchant_info.fc};{merchant_info.vat};a;v;c;s;w;d;f;e;{merchant_info.iban}')

    return merchants_csv


def euros_to_cents(amount):
    amount = round(float(amount), 2)
    return int(amount * 100)
