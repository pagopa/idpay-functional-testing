"""Offline checks that fast authorization scenarios cannot hide download failures."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bdd.steps import report_steps


class ReportDownloadAccessTest(unittest.TestCase):
    def test_access_check_calls_download_once_without_polling(self):
        context = SimpleNamespace(initiative_id='initiative',
                                  latest_report_request_id='report',
                                  report_access_token='token')
        response = Mock(status_code=400)
        with patch.object(report_steps, 'get_report_download', return_value=response) as download, \
             patch.object(report_steps, 'get_reports') as reports, \
             patch.object(report_steps.time, 'sleep') as sleep:
            report_steps.step_operator_checks_csv_report_download_access(context)
        download.assert_called_once_with(initiative_id='initiative', report_id='report',
                                         access_token='token')
        self.assertIs(context.latest_report_download_response, response)
        reports.assert_not_called()
        sleep.assert_not_called()

    def test_authorized_response_can_be_ready_or_not_generated_yet(self):
        for status, body in ((200, {}), (400, {'code': 'REPORT_NOT_GENERATED'})):
            with self.subTest(status=status):
                response = Mock(status_code=status, content=b'report', text=str(body))
                response.json.return_value = body
                report_steps.step_operator_is_authorized_to_download_csv_report(
                    SimpleNamespace(latest_report_download_response=response))

    def test_access_check_rejects_denials_and_unrelated_errors(self):
        for status, body, content in (
            (401, {}, b'error'),
            (403, {}, b'error'),
            (404, {'code': 'REPORT_NOT_FOUND'}, b'error'),
            (400, {'code': 'INVALID_ORGANIZATION_ROLE'}, b'error'),
            (400, {}, b'error'),
            (500, {}, b'error'),
            (200, {}, b''),
        ):
            with self.subTest(status=status, body=body, content=content):
                response = Mock(status_code=status, content=content, text=str(body))
                response.json.return_value = body
                context = SimpleNamespace(latest_report_download_response=response)
                with self.assertRaises(AssertionError):
                    report_steps.step_operator_is_authorized_to_download_csv_report(context)
