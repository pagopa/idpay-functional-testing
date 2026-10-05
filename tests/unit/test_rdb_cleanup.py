"""End-of-run cleanup behavior, with every HTTP operation simulated."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from util import rdb_cleanup as cleanup_module


def response(status=200, body=None):
    return SimpleNamespace(status_code=status, json=lambda: body, text='"test-token"')


class CleanupTest(unittest.TestCase):
    def setUp(self):
        secret = Mock()
        secret.base_path.IDPAY.internal = 'https://internal.test/'
        settings = SimpleNamespace(TARGET_ENV='uat',
                                   IDPAY=SimpleNamespace(endpoints=SimpleNamespace(
                                       asset_register=SimpleNamespace(backend_path='/backend/idpay/register'))))
        self.patches = [patch.object(cleanup_module, 'secrets', secret),
                        patch.object(cleanup_module, 'settings', settings),
                        patch.object(cleanup_module.requests, 'request', return_value=response(
                            body=list(cleanup_module._CAPABILITIES)))]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        cleanup_module._active = None
        self.addCleanup(setattr, cleanup_module, '_active', None)
        self.cleanup = cleanup_module.Cleanup()
        self.cleanup.timeout = 2
        self.data = {'/files/find': [], '/products/find': []}
        self.cleanup.http = Mock(side_effect=self.http)
        self.cleanup.profiles['token'] = {'orgId': 'producer'}

    def http(self, method, path, allowed=(200, 204), **kwargs):
        if path == '/files/delete':
            self.data['/files/find'] = []
            return response(204)
        if path == '/associations/restore':
            value = kwargs['json']
            self.data['/associations/' + value['id']] = value['before']
            return response(204)
        if path == '/consents/delete':
            return response(204)
        value = self.data.get(path)
        return response(404 if value is None and method == 'GET' else 200, value)

    def prepare_file(self, filename='unique.csv'):
        return self.cleanup.before_file('token', 'initiative', (
            filename, b'Codice GTIN/EAN;Marca\nABC123;Brand\n', 'text/csv'))

    def test_shared_association_restores_original_snapshot_after_multiple_writes(self):
        path = '/associations/producer_initiative'
        before = {'id': 'producer_initiative', 'producerEmail': 'original', 'createdAt': 'original-date'}
        self.data[path] = before
        key = self.cleanup.before_association('producer', 'initiative')
        self.data[path] = {**before, 'producerEmail': 'first'}
        self.cleanup.after_association(key)
        self.cleanup.before_association('producer', 'initiative')
        self.data[path] = {**before, 'producerEmail': 'second'}
        self.cleanup.after_association(key)
        self.cleanup.clean()
        self.assertEqual(self.data[path], before)
        restore = next(call.kwargs['json'] for call in self.cleanup.http.call_args_list
                       if call.args[1] == '/associations/restore')
        self.assertEqual(restore['before'], before)
        self.assertEqual(restore['expected']['producerEmail'], 'second')

    def test_new_association_is_removed(self):
        key = self.cleanup.before_association('new', 'initiative')
        self.data['/associations/' + key] = {'id': key}
        self.cleanup.after_association(key)
        self.cleanup.clean()
        self.assertIsNone(self.data['/associations/' + key])

    def test_external_change_prevents_next_tracked_mutation(self):
        path = '/associations/producer_initiative'
        self.data[path] = {'email': 'original'}
        self.cleanup.before_association('producer', 'initiative')
        self.data[path] = {'email': 'external'}
        with self.assertRaisesRegex(cleanup_module.CleanupError, 'outside'):
            self.cleanup.before_association('producer', 'initiative')

    def test_preexisting_filename_is_rejected(self):
        self.data['/files/find'] = [{'id': 'existing'}]
        with self.assertRaisesRegex(cleanup_module.CleanupError, 'predates'):
            self.prepare_file()
        self.assertFalse(self.cleanup.files)

    def test_preexisting_product_in_any_organization_is_protected(self):
        self.data['/products/find'] = [{'id': 'existing-product', 'productFileId': 'foreign-file'}]
        with self.assertRaisesRegex(cleanup_module.CleanupError, 'pre-existing product'):
            self.prepare_file()
        self.assertFalse(self.cleanup.files)

    def test_reloading_product_created_by_this_run_is_allowed(self):
        self.cleanup.file_ids.add('own-file')
        self.data['/products/find'] = [{'productFileId': 'own-file'}]
        key = self.prepare_file('reload.csv')
        self.assertIn(key, self.cleanup.files)

    def test_invalid_csv_is_forwarded_and_recorded_for_formal_report_cleanup(self):
        key = self.cleanup.before_file('token', 'initiative', ('bad.csv', b'\xff', 'text/csv'))
        self.assertIn(key, self.cleanup.files)
        self.assertFalse(any(call.args[1] == '/products/find' for call in self.cleanup.http.call_args_list))

    def test_file_lookup_uses_exact_scope(self):
        key = self.prepare_file()
        self.assertEqual(self.cleanup.files[key], {
            'organizationId': 'producer', 'initiativeId': 'initiative', 'fileName': 'unique.csv'})
        self.assertIn({'initiativeId': 'initiative', 'gtinCodes': ['ABC123']},
                      [call.kwargs.get('json') for call in self.cleanup.http.call_args_list])

    def test_own_file_ids_are_recorded_after_upload(self):
        key = self.prepare_file()
        self.data['/files/find'] = [{'id': 'created-file'}]
        self.cleanup.after_file(key)
        self.assertEqual(self.cleanup.file_ids, {'created-file'})

    def test_files_are_deleted_before_associations(self):
        self.prepare_file()
        self.cleanup.before_association('producer', 'initiative')
        self.cleanup.clean()
        paths = [call.args[1] for call in self.cleanup.http.call_args_list]
        self.assertLess(paths.index('/files/delete'), paths.index('/associations/restore'))

    def test_file_failure_is_reported_and_association_is_retained(self):
        self.prepare_file()
        self.cleanup.before_association('producer', 'initiative')
        base = self.cleanup.http.side_effect
        def fail(method, path, **kwargs):
            if path == '/files/delete':
                raise cleanup_module.CleanupError('HTTP 503')
            return base(method, path, **kwargs)
        self.cleanup.http.side_effect = fail
        self.cleanup.consents.add('fresh-user')
        with self.assertRaisesRegex(cleanup_module.CleanupError, 'HTTP 503'):
            self.cleanup.clean()
        paths = [call.args[1] for call in self.cleanup.http.call_args_list]
        self.assertIn('/consents/delete', paths)
        self.assertNotIn('/associations/restore', paths)

    def test_processing_file_waits_then_cleans(self):
        scope = {'fileName': 'processing.csv'}
        self.cleanup.http = Mock(side_effect=[response(409),
                                              response(body=[{'uploadStatus': 'IN_PROCESS'}]),
                                              response(204), response(body=[])])
        with patch.object(cleanup_module.time, 'sleep') as sleep:
            self.cleanup.delete_file(scope)
            sleep.assert_called_once()

    def test_processing_timeout_fails_cleanup(self):
        self.cleanup.http = Mock(side_effect=[response(409), response(body=[{'uploadStatus': 'UPLOADED'}])])
        with patch.object(cleanup_module.time, 'monotonic', side_effect=[0, 3]):
            with self.assertRaisesRegex(cleanup_module.CleanupError, 'timeout'):
                self.cleanup.delete_file({'fileName': 'processing.csv'})

    def test_only_acknowledged_portal_initiative_ids_are_deleted(self):
        from api import idpay
        from util import rdb_utilities as rdb
        cleanup_module._active = self.cleanup
        cleanup_module.remember_portal('created', {'orgId': 'generated'})
        with patch.object(idpay, 'obtain_selfcare_test_token'), \
             patch.object(rdb, 'token_from_response', return_value='portal-token'), \
             patch.object(idpay, 'delete_initiative', return_value=response(204)) as delete, \
             patch.object(idpay, 'get_initiatives_summary', return_value=response(
                 body=[{'initiativeId': 'preexisting'}])):
            self.cleanup.clean()
            delete.assert_called_once_with('created', domain='/idpay')

    def test_portal_delete_uses_internal_route_and_preserves_default_for_other_suites(self):
        from api import idpay
        configuration = SimpleNamespace(default_timeout=30, IDPAY=SimpleNamespace(
            domain='/idpay-itn', endpoints=SimpleNamespace(
                initiatives=SimpleNamespace(portal='/portalbackend'))))
        secret = SimpleNamespace(base_path=SimpleNamespace(
            IDPAY=SimpleNamespace(internal='https://internal.test')))
        with patch.object(idpay, 'settings', configuration), \
             patch.object(idpay, 'secrets', secret), \
             patch.object(idpay.requests, 'delete', return_value=response(204)) as delete:
            idpay.delete_initiative('created', domain='/idpay')
            delete.assert_called_with('https://internal.test/portalbackend/idpay/initiative/created',
                                      timeout=30)
            idpay.delete_initiative('other-suite')
            delete.assert_called_with('https://internal.test/portalbackend/idpay-itn/initiative/other-suite',
                                      timeout=30)

    def test_cleanup_conflict_is_reported(self):
        self.cleanup.before_association('producer', 'initiative')
        base = self.cleanup.http.side_effect
        def fail(method, path, **kwargs):
            if path == '/associations/restore':
                raise cleanup_module.CleanupError('HTTP 409')
            return base(method, path, **kwargs)
        self.cleanup.http.side_effect = fail
        with self.assertRaisesRegex(cleanup_module.CleanupError, 'HTTP 409'):
            self.cleanup.clean()

    def test_finish_clears_run_state_even_when_cleanup_fails(self):
        cleanup_module._active = Mock()
        cleanup_module._active.clean.side_effect = cleanup_module.CleanupError('failure')
        with self.assertRaises(cleanup_module.CleanupError):
            cleanup_module.finish()
        self.assertIsNone(cleanup_module._active)

    def test_cleanup_does_not_require_dedicated_secret(self):
        cleanup_module.secrets.get.return_value = {}
        cleanup_module.Cleanup()
        cleanup_module.secrets.get.assert_not_called()
        self.assertEqual(cleanup_module.requests.request.call_count, 2)

    def test_production_is_rejected(self):
        cleanup_module.settings.TARGET_ENV = 'prod'
        with self.assertRaisesRegex(cleanup_module.CleanupError, 'dev/uat'):
            cleanup_module.Cleanup()

    def test_http_404_is_not_successful_deletion(self):
        cleanup_module.requests.request.return_value = response(404)
        with self.assertRaisesRegex(cleanup_module.CleanupError, 'HTTP 404'):
            cleanup_module.Cleanup.http(self.cleanup, 'POST', '/files/delete')

    def test_requests_do_not_send_dedicated_credential_or_follow_redirects(self):
        call = cleanup_module.requests.request.call_args
        self.assertNotIn('headers', call.kwargs)
        self.assertFalse(call.kwargs['allow_redirects'])

    def test_tracking_decorator_preserves_result_and_records_outcome(self):
        cleanup_module._active = self.cleanup
        @cleanup_module.tracked('import')
        def import_records(producers):
            self.data['/associations/new_initiative'] = {'id': 'new_initiative'}
            return 'original-result'
        self.assertEqual(import_records([{'producerId': 'new', 'initiativeId': 'initiative'}]),
                         'original-result')
        self.assertEqual(self.cleanup.associations['new_initiative']['expected'], {'id': 'new_initiative'})

    def test_tracking_decorator_records_successful_write_even_if_caller_raises(self):
        cleanup_module._active = self.cleanup
        @cleanup_module.tracked('email')
        def update(organization_id, initiative_id):
            self.data['/associations/producer_initiative'] = {'email': 'changed'}
            raise ValueError('caller failure')
        with self.assertRaisesRegex(ValueError, 'caller failure'):
            update('producer', 'initiative')
        self.assertEqual(self.cleanup.associations['producer_initiative']['expected'], {'email': 'changed'})

    def test_untracked_suites_send_original_request_without_cleanup(self):
        called = Mock(return_value='original')
        self.assertEqual(cleanup_module.tracked('file')(called)('token', 'initiative', 'csv'), 'original')
        called.assert_called_once_with('token', 'initiative', 'csv')


if __name__ == '__main__':
    unittest.main()
