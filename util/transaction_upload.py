"""Utility class to upload transaction files.
"""
from datetime import datetime

from api.rtd import public_key, sas_token, upload_file
from util.encrypt_utilities import pgp_file_routine

TRANSACTION_FILE_EXTENSION = "csv"
APPLICATION_PREFIX_FILE_NAME = "CSTAR"
TRANSACTION_LOG_FIXED_SEGMENT = "TRNLOG"
CHECKSUM_PREFIX = "#sha256sum:"


def encrypt_and_upload(transactions: str):
    """Utility to encrypt and upload transactions.
    :param transactions: content of transaction file to be encrypted and uploaded.
    :returns: the response of the upload.
    :rtype: requests.Response
    """
    input_file_name = input_trx_name_formatter('IDPAY')
    with open(input_file_name, 'w') as f:
        f.write(transactions)
    pub_key = public_key()
    encrypted_file_path = pgp_file_routine(input_file_name, pub_key.text)
    res = sas_token()
    sas = res.json()['sas']
    authorized_container = res.json()['authorizedContainer']
    res = upload_file(authorized_container, encrypted_file_path, sas)

    return res, input_file_name


def input_trx_name_formatter(sender_code: str):
    """Given a sender code return a string compliant with Batch Service output file.
    :param sender_code: sender code in the name.
    :returns: well formatted output file name.
    :rtype: str
    """
    return "{}.{}.{}.{}.001.01.{}".format(APPLICATION_PREFIX_FILE_NAME, sender_code, TRANSACTION_LOG_FIXED_SEGMENT,
                                          datetime.now().strftime('%Y%m%d.%H%M%S'),
                                          TRANSACTION_FILE_EXTENSION)
