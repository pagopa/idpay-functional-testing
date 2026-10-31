"""Offline checks of BDD report routing without remote configuration."""
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = (ROOT / '.github/workflows/test-run-bdd.yaml').read_text(encoding='utf-8')
DISPATCH = (ROOT / '.github/workflows/test-run.yaml').read_text(encoding='utf-8')
SANITIZER = ROOT / 'util/sanitize-allure-results.py'
INITIATIVES = ('bonus_elettrodomestici', 'bonus_decoder')


def sanitize_step():
    step = WORKFLOW.split('      - name: Sanitize allure results\n', 1)[1]
    step = step.split('\n      - ', 1)[0]
    return textwrap.dedent(step.split('        run: |\n', 1)[1])


class ReportTagRoutingTest(unittest.TestCase):
    def setUp(self):
        self.workspace = ROOT / f".report-tag-routing-{uuid.uuid4().hex}"
        self.workspace.mkdir()
        self.addCleanup(shutil.rmtree, self.workspace)
        self.results = self.workspace / 'allure-results'
        self.results.mkdir()
        self.result = self.results / 'example-result.json'
        self.arguments = self.workspace / 'arguments.txt'
        self.original = {
            'fullName': 'Scenario',
            'historyId': 'history',
            'testCaseId': 'case',
            'description': 'Bearer fake.token.signature',
            'labels': [{'name': 'parentSuite', 'value': 'original-suite'}],
        }
        self.result.write_text(json.dumps(self.original), encoding='utf-8')

    def run_sanitizer_step(self, tag):
        self.result.write_text(json.dumps(self.original), encoding='utf-8')
        wrapper = """
        python3() {
          printf '%s\\n' "$@" > "$REPORT_TEST_ARGUMENTS"
          shift
          "$REPORT_TEST_PYTHON" "$REPORT_TEST_SANITIZER" "$@"
        }
        """
        completed = subprocess.run(
            ['bash', '-e', '-c', textwrap.dedent(wrapper) + sanitize_step()],
            cwd=self.workspace,
            env={
                **os.environ,
                'FEATURE_TAG': tag,
                'REPORT_TEST_ARGUMENTS': str(self.arguments),
                'REPORT_TEST_PYTHON': sys.executable,
                'REPORT_TEST_SANITIZER': str(SANITIZER),
            },
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        arguments = self.arguments.read_text(encoding='utf-8').splitlines()
        result = json.loads(self.result.read_text(encoding='utf-8'))
        self.assertNotIn('fake.token.signature', result['description'])
        self.assertNotEqual(result['description'], self.original['description'])
        return arguments, result

    def test_initiative_tags_keep_suite_and_history_identity(self):
        for tag, suite in zip(INITIATIVES, ('Bonus Elettrodomestici', 'Bonus Decoder')):
            with self.subTest(tag=tag):
                arguments, result = self.run_sanitizer_step(tag)
                self.assertEqual(
                    arguments,
                    ['util/sanitize-allure-results.py', 'allure-results', '--initiative', tag],
                )
                self.assertIn({'name': 'initiative', 'value': tag}, result['labels'])
                self.assertIn({'name': 'parentSuite', 'value': suite}, result['labels'])
                for field in ('fullName', 'historyId', 'testCaseId'):
                    self.assertEqual(result[field], f"{tag}:{self.original[field]}")

    def test_scenario_tags_and_all_redact_without_inventing_an_initiative(self):
        feature_input = DISPATCH.split('      feature:\n', 1)[1]
        feature_input = feature_input.split('\n      environment:', 1)[0]
        tags = re.findall(r'^\s+- ([a-z_]+)$', feature_input, re.MULTILINE)
        self.assertIn('reward_batch_counter', tags)
        self.assertIn('all', tags)
        for tag in tags + ['arbitrary_tag', 'reward_batch_counter or bonus_decoder']:
            if tag in INITIATIVES:
                continue
            with self.subTest(tag=tag):
                arguments, result = self.run_sanitizer_step(tag)
                self.assertEqual(arguments, ['util/sanitize-allure-results.py', 'allure-results'])
                self.assertEqual(result['labels'], self.original['labels'])
                for field in ('fullName', 'historyId', 'testCaseId'):
                    self.assertEqual(result[field], self.original[field])

    def test_all_dispatch_preserves_the_existing_two_initiative_matrix(self):
        self.assertIn(
            "tag: ${{ inputs.feature_tag == 'all' && "
            """fromJson('["bonus_elettrodomestici", "bonus_decoder"]') || """
            """fromJson(format('["{0}"]', inputs.feature_tag)) }}""",
            WORKFLOW,
        )

    def test_behave_still_uses_feature_tag_as_the_filter(self):
        self.assertIn('--tags "$FEATURE_TAG" \\', WORKFLOW)

    def test_missing_results_does_not_invoke_sanitizer(self):
        shutil.rmtree(self.results)
        completed = subprocess.run(
            ['bash', '-e', '-c', 'python3() { return 23; }\n' + sanitize_step()],
            cwd=self.workspace,
            env={**os.environ, 'FEATURE_TAG': 'reward_batch_counter'},
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('No allure-results directory to sanitize', completed.stdout)

    def test_sanitizer_failure_is_not_silently_ignored(self):
        completed = subprocess.run(
            ['bash', '-e', '-c', 'python3() { return 23; }\n' + sanitize_step()],
            cwd=self.workspace,
            env={**os.environ, 'FEATURE_TAG': 'reward_batch_counter'},
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 23)

    def test_sanitizer_cli_still_rejects_scenario_tags_as_initiatives(self):
        completed = subprocess.run(
            [
                sys.executable, str(SANITIZER), str(self.results),
                '--initiative', 'reward_batch_counter',
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn('invalid choice', completed.stderr)


if __name__ == '__main__':
    unittest.main()
