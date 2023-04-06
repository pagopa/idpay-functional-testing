import datetime
import math
import random
import uuid
from hashlib import sha256

from faker import Faker
from schwifty import IBAN
from six import unichr

from api.rtd import pm_salt

fake = Faker('it_IT')

circuits = ['visa', 'mastercard', 'maestro', 'amex']


def hash_pan(pan: str):
    """Function that hashes a PAN with salt got from the Payment Manager
    :param pan: Clear PAN to be encrypted.
    :returns:  The hashed  PAN.
    :rtype: str
    """
    salt = pm_salt()
    return sha256(f'{pan}{salt}'.encode()).hexdigest()


def fake_fc():
    """Faker wrapper that calls faker's ssn method and uses non-existing birthplace characters.
    :returns:  A fake fiscal code.
    :rtype: str
    """
    fake_cf = fake.ssn()
    return f'{fake_cf[:11]}X000{fake_cf[15:]}'


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
    return IBAN.generate('IT', bank_code=abi, account_code=str(round(random.random() * math.pow(10, 12)))).compact


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


def custom_transaction(pan: str,
                       amount: int,
                       correlation_id: str = None,
                       curr_date: str = None,
                       reversal: bool = False,
                       mcc: str = None):
    if not correlation_id:
        correlation_id = uuid.uuid4().int
    if not curr_date:
        curr_date = (datetime.datetime.utcnow() + datetime.timedelta(seconds=random.randint(10, 60))).strftime(
            '%Y-%m-%dT%H:%M:%S.000Z')
    if not mcc:
        mcc = '1234'

    return f'IDPAY;{"01" if reversal else "00"};00;{hash_pan(pan)};{curr_date};{uuid.uuid4().int};{uuid.uuid4().int};{correlation_id};{amount};978;12345;{uuid.uuid4().int};{uuid.uuid4().int};{pan[:8]};{mcc};{fake_fc()};{fake_vat()};00;{sha256(f"{pan}".encode()).hexdigest().upper()[:29]}'


def custom_transaction_json(pan: str,
                            amount: int,
                            correlation_id: str = None,
                            curr_date: str = None,
                            reversal: bool = False,
                            mcc: str = None):
    if not correlation_id:
        correlation_id = uuid.uuid4().int
    if not curr_date:
        curr_date = (datetime.datetime.utcnow() + datetime.timedelta(seconds=random.randint(10, 60))).strftime(
            '%Y-%m-%dT%H:%M:%S.000Z')
    if not mcc:
        mcc = '1234'

    transaction = {
        'circuitType': '00',
        'hpan': hash_pan(pan),
        'trxDate': curr_date,
        'idTrxAcquirer': uuid.uuid4().int,
        'idTrxIssuer': uuid.uuid4().int,
        'correlationId': correlation_id,
        'amount': amount,
        'amountCurrency': '978',
        'acquirerId': '12345',
        'merchantId': uuid.uuid4().int,
        'terminalId': uuid.uuid4().int,
        'bin': pan[:8],
        'mcc': mcc,
        'fiscalCode': fake_fc(),
        'vat': fake_vat(),
        'posType': '00',
        'par': sha256(f'{pan}'.encode()).hexdigest().upper()[:29],
        'acquirerCode': 'IDPAY',
        'operationType': '01' if reversal else '00'
    }
    return transaction
