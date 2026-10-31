"""Offline reward-batch integration checks; use the safe template configuration."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import requests

from api import transaction
from bdd.steps import reward_batch_steps
from model.transaction_model import TransactionActionRequest
from util import transaction_utilities


def response(body=None, status=200):
    return SimpleNamespace(status_code=status, json=lambda: body, text='')


class RewardBatchIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.network = patch.object(
            requests.sessions.Session,
            'request',
            side_effect=AssertionError('Network access prohibited in offline tests'),
        )
        self.network.start()
        self.addCleanup(self.network.stop)
        self.context = SimpleNamespace(
            initiative_name='bonus_elettrodomestici',
            initiative_id='initiative',
            associated_merchant={'X': '1'},
            merchants={'1': {'id': 'merchant'}},
            transactions={'X': {'id': 'transaction'}},
            transaction_pos_access_tokens={'X': 'test-pos-token'},
            reward_batch_ids={'X': 'source'},
            reward_batches_to_cleanup={('initiative', 'merchant', 'source')},
        )

    def test_postpone_retains_source_and_registers_next_month_for_cleanup(self):
        for month in range(1, 13):
            with self.subTest(month=month):
                source = {
                    'id': 'source', 'status': 'CREATED',
                    'month': f'2026-{month:02d}',
                }
                destination = {
                    'id': 'destination', 'status': 'CREATED',
                    'month': '2027-01' if month == 12 else f'2026-{month + 1:02d}',
                }
                self.context.reward_batches_to_cleanup = {
                    ('initiative', 'merchant', 'source'),
                }
                with (
                    patch.object(reward_batch_steps, 'get_merchant_access_token',
                                 return_value='test-merchant-token'),
                    patch.object(reward_batch_steps, '_get_reward_batch_transactions',
                                 return_value=[{'trxId': 'transaction'}]),
                    patch.object(reward_batch_steps, 'get_reward_batch_detail',
                                 side_effect=[response(source), response(destination)]),
                    patch.object(reward_batch_steps, 'post_postpone_transaction',
                                 autospec=True, return_value=response(status=204)) as postpone,
                    patch.object(reward_batch_steps, 'retry_reward_batch_reassignment',
                                 return_value={'rewardBatchId': 'destination'}),
                ):
                    reward_batch_steps.step_postpone_transaction_to_next_reward_batch(
                        self.context, '1', 'X'
                    )
                postpone.assert_called_once_with(
                    initiative_id='initiative', reward_batch_id='source',
                    transaction_id='transaction', access_token='test-merchant-token',
                )
                self.assertEqual(self.context.reward_batch_ids['X'], 'source')
                self.assertEqual(self.context.source_reward_batches['X'], source)
                self.assertEqual(self.context.destination_reward_batches['X'], destination)
                self.assertEqual(self.context.reward_batches_to_cleanup, {
                    ('initiative', 'merchant', 'source'),
                    ('initiative', 'merchant', 'destination'),
                })

    def test_invoice_and_approval_destinations_are_registered_even_if_final_check_fails(self):
        for status, actual_status in (
            ('EVALUATING', 'EVALUATING'),
            ('APPROVED', 'APPROVED'),
            ('APPROVED', 'APPROVING'),
        ):
            with self.subTest(status=status, actual_status=actual_status):
                source = {'id': 'source', 'status': actual_status, 'posType': 'PHYSICAL'}
                destination = {
                    'id': 'destination', 'status': 'CREATED', 'posType': 'PHYSICAL',
                    'initiativeId': 'initiative', 'merchantId': 'merchant',
                    'month': '2026-10',
                }
                self.context.source_reward_batches = {'X': source}
                self.context.reward_batches_to_cleanup = {
                    ('initiative', 'merchant', 'source'),
                }
                with (
                    patch.object(reward_batch_steps, 'retry_reward_batch_reassignment',
                                 return_value={'rewardBatchId': 'destination'}),
                    patch.object(reward_batch_steps, 'get_reward_batch_detail',
                                 side_effect=[response(destination), response(source)]),
                ):
                    if status == actual_status:
                        reward_batch_steps._assert_transaction_is_reassigned_to_reward_batch(
                            self.context, 'X', 'SUSPENDED', {'2026-10'}, status
                        )
                    else:
                        with self.assertRaises(AssertionError):
                            reward_batch_steps._assert_transaction_is_reassigned_to_reward_batch(
                                self.context, 'X', 'SUSPENDED', {'2026-10'}, status
                            )
                self.assertIn(
                    ('initiative', 'merchant', 'destination'),
                    self.context.reward_batches_to_cleanup,
                )

    def test_action_callers_use_the_access_token_api_signature(self):
        for action in ('approve', 'reject', 'suspend'):
            with self.subTest(action=action):
                api_name = f'post_{action}_transactions'
                with patch.object(
                    transaction_utilities, api_name, autospec=True,
                    return_value=response(),
                ) as api_call:
                    transaction_utilities.perform_reward_batch_transaction_action(
                        'initiative', 'source', 'test-operator-token', 'transaction', action
                    )
                self.assertEqual(api_call.call_args.kwargs['access_token'], 'test-operator-token')
                self.assertEqual(
                    api_call.call_args.kwargs['transaction_action_request'].transaction_ids,
                    ['transaction'],
                )
        with patch.object(
            transaction_utilities, 'post_validate_reward_batch', autospec=True,
            return_value=response(),
        ) as validate:
            transaction_utilities.validate_reward_batch_as_operator(
                'initiative', 'source', 'test-operator-token'
            )
            transaction_utilities.request_reward_batch_validation(
                'initiative', 'source', 'test-operator-token'
            )
        self.assertEqual(validate.call_count, 2)

    def test_reward_batch_apis_forward_access_token_and_configured_postpone_path(self):
        arguments = {
            'initiative_id': 'initiative', 'reward_batch_id': 'source',
            'access_token': 'test-operator-token',
        }
        for name in (
            'post_approve_transactions', 'post_reject_transactions',
            'post_suspend_transactions', 'post_approve_reward_batch',
            'post_validate_reward_batch', 'post_postpone_transaction',
        ):
            with self.subTest(api=name):
                kwargs = dict(arguments)
                if name.endswith('_transactions'):
                    kwargs['transaction_action_request'] = TransactionActionRequest(
                        transaction_ids=['transaction']
                    )
                if name == 'post_postpone_transaction':
                    kwargs['transaction_id'] = 'transaction'
                with patch.object(requests, 'post', return_value=response()) as post:
                    getattr(transaction, name)(**kwargs)
                self.assertIn('test-operator-token', post.call_args.kwargs['headers']['Authorization'])
                if name == 'post_postpone_transaction':
                    self.assertTrue(post.call_args.args[0].endswith(
                        '/merchant/portal/initiatives/initiative/reward-batches/source'
                        '/transactions/transaction/postpone'
                    ))


if __name__ == '__main__':
    unittest.main()
