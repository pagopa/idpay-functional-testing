"""Track this run's RDB fixtures in memory and clean them through HTTP APIs."""
import csv
import inspect
import io
import threading
import time
from functools import wraps

import requests

from conf.configuration import secrets
from conf.configuration import settings

_ACTIVE_STATUSES = {'UPLOADED', 'IN_PROCESS'}
_CLEANUP_TIMEOUT = 120
_CAPABILITIES = {'files-v1', 'products-v1', 'association-cas-v1', 'consents-v1'}
_active = None
_pending = []
_verified_base = None


class CleanupError(RuntimeError):
    pass


class Cleanup:
    def __init__(self):
        if str(settings.TARGET_ENV).lower() not in ('dev', 'uat'):
            raise CleanupError('RDB fixture cleanup is supported only in dev/uat')
        backend = secrets.base_path.IDPAY.internal.rstrip('/')
        register = backend + settings.IDPAY.endpoints.asset_register.backend_path
        self.base = register + '/clean/fixtures'
        self.profiles = {}
        self.files = {}
        self.associations = set()
        self.producers = set()
        self.consents = set()
        self.portal_initiatives = {}
        self.lock = threading.RLock()
        self.timeout = _CLEANUP_TIMEOUT
        global _verified_base
        if _verified_base != self.base:
            capabilities = self.http('GET', '/capabilities').json()
            if not _CAPABILITIES <= set(capabilities):
                raise CleanupError('Deploy and enable the fixture cleanup API before running RDB tests')
            _verified_base = self.base

    def http(self, method, path, allowed=(200, 204), **kwargs):
        response = requests.request(method, self.base + path, timeout=(10, 30),
                                    allow_redirects=False, **kwargs)
        if response.status_code not in allowed:
            raise CleanupError(f'Cleanup {method} {path}: HTTP {response.status_code}')
        return response

    def association(self, key):
        response = self.http('GET', '/associations/' + key, allowed=(200, 404))
        return None if response.status_code == 404 else response.json()

    def find_files(self, scope):
        return self.http('POST', '/files/find', json=scope).json()

    def before_association(self, producer, initiative):
        if not producer or not initiative:
            return  # Missing-field scenarios must reach the import service.
        if producer not in self.producers:
            raise CleanupError('Association writes require a scenario-owned producer')
        self.associations.add(producer + '_' + initiative)

    def before_import(self, producers):
        for producer in producers:
            if isinstance(producer, dict):
                self.before_association(producer.get('producerId'), producer.get('initiativeId'))

    def before_file(self, token, initiative, csv_file):
        from util.asset_register_utilities import _build_csv_file_part
        name, content, *_ = _build_csv_file_part(csv_file)
        with self.lock:
            organization = self.profiles.get(token)
            if organization is None:
                raise CleanupError('CSV writer has no tracked test profile')
            scope = {'organizationId': organization, 'initiativeId': initiative, 'fileName': name}
            key = (organization, initiative, name)
            if key in self.files:
                return key
            if self.find_files(scope):
                raise CleanupError('Refusing to reuse a CSV that predates this run')
            codes = _gtin_codes(content)
            if codes:
                products = self.http('POST', '/products/find', json={
                    'initiativeId': initiative, 'gtinCodes': codes}).json()
                owned_files = set()
                if products:
                    for prior_scope in self.files.values():
                        owned_files.update(file['id'] for file in self.find_files(prior_scope))
                if any(product.get('productFileId') not in owned_files for product in products):
                    raise CleanupError('CSV would modify a pre-existing product; no upload sent')
            self.files[key] = scope
            return key

    def delete_file(self, scope):
        deadline = time.monotonic() + self.timeout
        while True:
            response = self.http('POST', '/files/delete', allowed=(204, 409), json=scope)
            files = self.find_files(scope)
            if response.status_code == 204:
                if files:
                    raise CleanupError('Upload still present after cleanup')
                return
            if not any(file.get('uploadStatus') in _ACTIVE_STATUSES for file in files):
                raise CleanupError('File cleanup conflict')
            _wait(deadline, 'Upload still processing at cleanup timeout')

    def delete_portal_initiative(self, initiative_id, token):
        from api import idpay
        from util import rdb_utilities as rdb
        response = idpay.delete_initiative(initiative_id, domain='/idpay')
        if response.status_code not in (200, 202, 204, 404):
            raise CleanupError(f'Portal initiative deletion: HTTP {response.status_code}')
        deadline = time.monotonic() + self.timeout
        while True:
            initiatives = rdb.success(idpay.get_initiatives_summary(token)).json()
            if all(item['initiativeId'] != initiative_id for item in initiatives):
                del self.portal_initiatives[initiative_id]
                return
            _wait(deadline, 'Portal initiative deletion still processing')

    def _delete_run_file(self, key, scope):
        self.delete_file(scope)
        del self.files[key]

    def _delete_consent(self, user_id):
        self.http('POST', '/consents/delete', allowed=(204,), json={'userId': user_id})
        self.consents.remove(user_id)

    def _delete_association(self, key):
        # The backend CAS contract requires the current document at deletion.
        expected = self.association(key)
        self.http('POST', '/associations/restore',
                  json={'id': key, 'before': None, 'expected': expected})
        if self.association(key) is not None:
            raise CleanupError('Association still present after cleanup')
        self.associations.remove(key)

    @staticmethod
    def _attempt(errors, label, function, *args):
        try:
            function(*args)
        except Exception as error:
            errors.append(f'{label}: {type(error).__name__}: {error}')

    def clean(self):
        errors = []
        for key, scope in self.files.copy().items():
            self._attempt(errors, f'file {scope["fileName"]}', self._delete_run_file, key, scope)
        for user_id in self.consents.copy():
            self._attempt(errors, f'consent {user_id}', self._delete_consent, user_id)
        for initiative_id, token in self.portal_initiatives.copy().items():
            self._attempt(errors, f'portal initiative {initiative_id}',
                          self.delete_portal_initiative, initiative_id, token)
        if self.files:
            errors.append('Associations retained because some run uploads could not be deleted')
        else:
            for key in self.associations.copy():
                self._attempt(errors, f'association {key}', self._delete_association, key)
        if errors:
            raise CleanupError('RDB fixture cleanup failed: ' + '; '.join(errors))
        print('RDB fixture cleanup completed')


def _gtin_codes(content):
    try:
        rows = csv.DictReader(io.StringIO(content.decode('utf-8-sig')), delimiter=';')
        return sorted({row.get('Codice GTIN/EAN') for row in rows} - {None, ''})
    except (UnicodeError, csv.Error):
        return []  # Malformed input still reaches the CSV validator.


def _wait(deadline, message):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise CleanupError(message)
    time.sleep(min(2, remaining))


def tracked(operation):
    def decorate(function):
        signature = inspect.signature(function)

        @wraps(function)
        def invoke(*args, **kwargs):
            cleanup = _active
            if cleanup is None:
                return function(*args, **kwargs)
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            values = bound.arguments
            if operation == 'file':
                cleanup.before_file(values['token'], values['initiative_id'], values['csv_file'])
            elif operation == 'import':
                cleanup.before_import(values['producers'])
            elif operation == 'email':
                cleanup.before_association(values['organization_id'], values['initiative_id'])
            result = function(*args, **kwargs)
            if operation == 'token' and result.status_code == 200:
                cleanup.profiles[result.text.strip().strip('"')] = values['body']['orgId']
            return result
        return invoke
    return decorate


def prepare_upload(token, initiative_id, csv_file):
    """Run ownership checks before a timing-sensitive upload starts."""
    if _active is not None:
        _active.before_file(token, initiative_id, csv_file)


def remember_portal(initiative_id, token):
    if _active is not None:
        _active.portal_initiatives[initiative_id] = token


def remember_consent(user_id):
    if _active is not None:
        _active.consents.add(user_id)


def remember_producer(organization_id):
    if _active is not None:
        _active.producers.add(organization_id)


def start(context=None):
    global _active
    if _active is None:
        _active = Cleanup()
    if context is not None:
        context.rdb_cleanup = _active


def finish_scenario():
    global _active
    cleanup, _active = _active, None
    if cleanup is not None:
        try:
            cleanup.clean()
        except Exception:
            _pending.append(cleanup)
            raise


def finish():
    global _active, _verified_base
    cleanup, _active = _active, None
    if cleanup is not None:
        _pending.append(cleanup)
    errors = []
    for item in _pending.copy():
        try:
            item.clean()
            _pending.remove(item)
        except Exception as error:
            errors.append(str(error))
    _verified_base = None
    if errors:
        raise CleanupError('; '.join(errors))
