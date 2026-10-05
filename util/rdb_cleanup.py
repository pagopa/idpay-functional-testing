"""Track this run's RDB fixtures in memory and clean them through HTTP APIs."""
import csv
import inspect
import io
import threading
import time
from copy import deepcopy
from functools import wraps

import requests
from conf.configuration import secrets, settings

_ACTIVE_STATUSES = {"UPLOADED", "IN_PROCESS"}
_CLEANUP_TIMEOUT = 120
_CAPABILITIES = {"files-v1", "products-v1", "association-cas-v1", "consents-v1"}
_active = None


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
        self.file_ids = set()
        self.associations = {}
        self.consents = set()
        self.portal_initiatives = {}
        self.lock = threading.RLock()
        self.timeout = _CLEANUP_TIMEOUT
        capabilities = self.http('GET', '/capabilities').json()
        if not _CAPABILITIES <= set(capabilities):
            raise CleanupError('Deploy and enable the fixture cleanup API before running RDB tests')

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
            return None  # Missing-field scenarios must reach the import service.
        key = producer + '_' + initiative
        with self.lock:
            current = self.association(key)
            entry = self.associations.get(key)
            if entry is None:
                self.associations[key] = {'before': deepcopy(current), 'expected': current}
            elif entry['expected'] != current:
                raise CleanupError('Association changed outside the tracked operation')
        return key

    def after_association(self, key):
        if key:
            with self.lock:
                self.associations[key]['expected'] = self.association(key)

    def before_file(self, token, initiative, csv_file):
        from util.asset_register_utilities import _build_csv_file_part
        name, content, *_ = _build_csv_file_part(csv_file)
        with self.lock:
            body = self.profiles.get(token)
            if body is None:
                raise CleanupError('CSV writer has no tracked test profile')
            scope = dict(organizationId=body['orgId'], initiativeId=initiative, fileName=name)
            key = (body['orgId'], initiative, name)
            if key in self.files:
                return key
            if self.find_files(scope):
                raise CleanupError('Refusing to reuse a CSV that predates this run')
            codes = _gtin_codes(content)
            if codes:
                products = self.http('POST', '/products/find', json={
                    'initiativeId': initiative, 'gtinCodes': codes}).json()
                if any(product.get('productFileId') not in self.file_ids for product in products):
                    raise CleanupError('CSV would modify a pre-existing product; no upload sent')
            self.files[key] = scope
            return key

    def after_file(self, key):
        with self.lock:
            files = self.find_files(self.files[key])
            self.file_ids.update(file['id'] for file in files)

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

    def delete_portal_initiative(self, initiative_id, body):
        from api import idpay
        from util import rdb_utilities as rdb
        token = rdb.token_from_response(idpay.obtain_selfcare_test_token(body))
        response = idpay.delete_initiative(initiative_id, domain='/idpay')
        if response.status_code not in (200, 202, 204, 404):
            raise CleanupError(f'Portal initiative deletion: HTTP {response.status_code}')
        deadline = time.monotonic() + self.timeout
        while True:
            initiatives = rdb.success(idpay.get_initiatives_summary(token)).json()
            if all(item['initiativeId'] != initiative_id for item in initiatives):
                return
            _wait(deadline, 'Portal initiative deletion still processing')

    def _delete_run_file(self, key, scope):
        self.delete_file(scope)
        del self.files[key]

    def _delete_consent(self, user_id):
        self.http('POST', '/consents/delete', allowed=(204,), json={'userId': user_id})

    def _restore_association(self, key, entry):
        self.http('POST', '/associations/restore', json={'id': key, **entry})
        if self.association(key) != entry['before']:
            raise CleanupError('Association differs from its initial state')

    @staticmethod
    def _attempt(errors, label, function, *args):
        try:
            function(*args)
        except Exception as error:
            errors.append(f'{label}: {type(error).__name__}: {error}')

    def clean(self):
        errors = []
        for key, scope in list(self.files.items()):
            self._attempt(errors, f'file {scope["fileName"]}', self._delete_run_file, key, scope)
        for user_id in self.consents:
            self._attempt(errors, f'consent {user_id}', self._delete_consent, user_id)
        for initiative_id, body in self.portal_initiatives.items():
            self._attempt(errors, f'portal initiative {initiative_id}',
                          self.delete_portal_initiative, initiative_id, body)
        if self.files:
            errors.append('Associations retained because some run uploads could not be deleted')
        else:
            for key, entry in self.associations.items():
                self._attempt(errors, f'association {key}', self._restore_association, key, entry)
        if errors:
            raise CleanupError('RDB end-of-suite cleanup failed: ' + '; '.join(errors))
        print('RDB end-of-suite cleanup completed')


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
            keys = []
            file_key = None
            if operation == 'file':
                file_key = cleanup.before_file(values['token'], values['initiative_id'], values['csv_file'])
            elif operation == 'import':
                pairs = dict.fromkeys((p.get('producerId'), p.get('initiativeId'))
                                      for p in values['producers'] if isinstance(p, dict))
                keys = [cleanup.before_association(*pair) for pair in pairs]
            elif operation == 'email':
                keys = [cleanup.before_association(values['organization_id'], values['initiative_id'])]
            try:
                result = function(*args, **kwargs)
            except Exception as error:
                try:
                    _after_write(cleanup, keys, file_key)
                except Exception as cleanup_error:
                    error.add_note(f'Unable to observe the write outcome ({type(cleanup_error).__name__})')
                raise
            _after_write(cleanup, keys, file_key)
            if operation == 'token' and result.status_code == 200:
                with cleanup.lock:
                    cleanup.profiles[result.text.strip().strip('"')] = dict(values['body'])
            return result
        return invoke
    return decorate


def _after_write(cleanup, keys, file_key):
    for key in keys:
        cleanup.after_association(key)
    if file_key is not None:
        cleanup.after_file(file_key)


def remember_portal(initiative_id, body):
    if _active is not None:
        _active.portal_initiatives[initiative_id] = dict(body)


def remember_consent(user_id):
    if _active is not None:
        _active.consents.add(user_id)


def start():
    global _active
    if _active is None:
        _active = Cleanup()


def finish():
    global _active
    cleanup, _active = _active, None
    if cleanup is not None:
        cleanup.clean()
