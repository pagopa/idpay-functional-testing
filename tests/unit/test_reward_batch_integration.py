"""Offline reward-batch integration checks; use the safe template configuration."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import requests

from api import transaction
from bdd.steps import bar_code_steps
from bdd.steps import reward_batch_counter_steps
from bdd.steps import reward_batch_steps
from model.transaction_model import ChecksErrorDTO
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
                                 return_value=response(source)),
                    patch.object(transaction_utilities, 'get_reward_batch_detail',
                                 side_effect=[response(source), response(destination)]),
                    patch.object(transaction_utilities, 'get_reward_batch_transactions',
                                 return_value=[{'trxId': 'transaction'}]),
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

    def test_postpone_checks_destination_membership_and_registers_it_before_failure(self):
        source = {"id": "source", "status": "CREATED", "month": "2026-12"}
        destination = {"id": "destination", "status": "CREATED", "month": "2027-01"}
        with (
            patch.object(reward_batch_steps, "get_merchant_access_token",
                         return_value="test-merchant-token"),
            patch.object(reward_batch_steps, "_get_reward_batch_transactions",
                         return_value=[{"trxId": "transaction"}]),
            patch.object(reward_batch_steps, "get_reward_batch_detail",
                         return_value=response(source)),
            patch.object(reward_batch_steps, "post_postpone_transaction",
                         return_value=response(status=204)),
            patch.object(reward_batch_steps, "retry_reward_batch_reassignment",
                         return_value={"rewardBatchId": "destination"}),
            patch.object(transaction_utilities, "get_reward_batch_detail",
                         side_effect=[response(source), response(destination)]),
            patch.object(transaction_utilities, "get_reward_batch_transactions",
                         return_value=[]),
            self.assertRaisesRegex(AssertionError, "not found in next reward batch"),
        ):
            reward_batch_steps.step_postpone_transaction_to_next_reward_batch(
                self.context, "1", "X"
            )
        self.assertIn(
            ("initiative", "merchant", "destination"),
            self.context.reward_batches_to_cleanup,
        )

    def test_counter_observation_reuses_pagination_with_one_merchant_token(self):
        rows = [
            {"trxId": "transaction", "rewardAmountCents": 6000},
            {"trxId": "other", "rewardAmountCents": 4000},
        ]
        with (
            patch.object(reward_batch_counter_steps, "get_reward_batch_detail",
                         return_value=response({"id": "source"})),
            patch.object(reward_batch_counter_steps, "get_merchant_access_token",
                         return_value="test-merchant-token") as token,
            patch.object(transaction_utilities, "get_merchant_processed_transactions",
                         side_effect=[
                             response({"content": rows[:1], "totalPages": 2}),
                             response({"content": rows[1:], "totalPages": 2}),
                         ]) as processed,
        ):
            _, transactions = reward_batch_counter_steps._batch_observation(
                self.context, "X"
            )
        self.assertEqual(transactions, rows)
        token.assert_called_once_with(
            initiative_name="bonus_elettrodomestici", merchant_name="1"
        )
        self.assertEqual(
            [call.kwargs["page"] for call in processed.call_args_list], [0, 1]
        )
        for call in processed.call_args_list:
            self.assertEqual(call.kwargs["reward_batch_id"], "source")
            self.assertEqual(call.kwargs["access_token"], "test-merchant-token")

    def test_successful_reversal_retains_the_token_for_eligibility_checks(self):
        with (
            patch.object(bar_code_steps, "get_point_of_sale_access_token",
                         return_value="refreshed-pos-token"),
            patch.object(bar_code_steps, "reverse_bar_code_transaction",
                         return_value=response(status=204)) as reverse,
        ):
            bar_code_steps.step_point_of_sale_reversal_bar_code(
                self.context, "pos_1", "1", "X"
            )
        reverse.assert_called_once_with(
            initiative_id="initiative", transaction_id="transaction",
            access_token="refreshed-pos-token",
        )
        self.assertEqual(
            self.context.transaction_pos_access_tokens["X"], "refreshed-pos-token"
        )

    def test_rejection_requires_the_target_transaction_to_be_rejected(self):
        for target_status in ("APPROVED", "TO_CHECK", None, "REJECTED"):
            with self.subTest(target_status=target_status):
                rows = [{"trxId": "other", "rewardBatchTrxStatus": "REJECTED"}]
                if target_status is not None:
                    rows.append({
                        "trxId": "transaction", "rewardBatchTrxStatus": target_status,
                    })
                with (
                    patch.object(reward_batch_counter_steps, "_batch_observation",
                                 return_value=({}, rows)),
                    patch.object(reward_batch_counter_steps.time, "sleep"),
                ):
                    if target_status == "REJECTED":
                        reward_batch_counter_steps.step_reward_batch_transaction_is_rejected(
                            self.context, "X"
                        )
                    else:
                        with self.assertRaisesRegex(AssertionError, "to be REJECTED"):
                            reward_batch_counter_steps.step_reward_batch_transaction_is_rejected(
                                self.context, "X"
                            )

    def test_rejection_waits_for_transition_and_checks_its_counter_contribution(self):
        before = [{"trxId": "transaction", "rewardBatchTrxStatus": "APPROVED",
                   "rewardAmountCents": 6000}]
        after = [{**before[0], "rewardBatchTrxStatus": "REJECTED"}]
        batch = {
            "id": "source", "status": "EVALUATING",
            "numberOfTransactions": 1, "numberOfTransactionsElaborated": 1,
            "numberOfTransactionsSuspended": 0, "numberOfTransactionsRejected": 1,
            "currentAmountCents": 6000, "excludedAmountCents": 6000,
            "approvedAmountCents": 0, "suspendedAmountCents": 0,
        }
        with (
            patch.object(reward_batch_counter_steps, "_batch_observation",
                         side_effect=[(batch, before), (batch, after)]) as observe,
            patch.object(reward_batch_counter_steps.time, "sleep"),
        ):
            reward_batch_counter_steps.step_reward_batch_transaction_is_rejected(
                self.context, "X"
            )
        self.assertEqual(observe.call_count, 2)
        for rejected_count, excluded_amount in ((0, 6000), (1, 0), (1, 6000)):
            with self.subTest(count=rejected_count, amount=excluded_amount):
                actual = {
                    **batch, "numberOfTransactionsRejected": rejected_count,
                    "excludedAmountCents": excluded_amount,
                }
                with (
                    patch.object(reward_batch_counter_steps, "_batch_observation",
                                 return_value=(actual, after)),
                    patch.object(reward_batch_counter_steps.time, "sleep"),
                ):
                    if rejected_count == 1 and excluded_amount == 6000:
                        reward_batch_counter_steps.step_live_reward_batch_counters_match(
                            self.context, "X"
                        )
                    else:
                        with self.assertRaisesRegex(AssertionError, "Differences"):
                            reward_batch_counter_steps.step_live_reward_batch_counters_match(
                                self.context, "X"
                            )

    def test_sent_snapshot_capture_checks_reward_sum_before_preserving_it(self):
        rows = [{"trxId": "transaction", "rewardBatchTrxStatus": "CONSULTABLE",
                 "rewardAmountCents": 6000}]
        batch = {
            "id": "source", "status": "SENT",
            "numberOfTransactions": 1, "numberOfTransactionsElaborated": 0,
            "numberOfTransactionsSuspended": 0, "numberOfTransactionsRejected": 0,
            "currentAmountCents": 6000, "excludedAmountCents": 0,
            "approvedAmountCents": 0, "suspendedAmountCents": 0,
        }
        for initial_amount in (0, 5000, 6000):
            with self.subTest(initial_amount=initial_amount):
                actual = {**batch, "initialAmountCents": initial_amount}
                with patch.object(reward_batch_counter_steps, "_batch_observation",
                                  return_value=(actual, rows)):
                    if initial_amount == 6000:
                        reward_batch_counter_steps.step_capture_reward_batch_counters(
                            self.context, "X", "after_send"
                        )
                    else:
                        with self.assertRaisesRegex(AssertionError, "initialAmountCents"):
                            reward_batch_counter_steps.step_capture_reward_batch_counters(
                                self.context, "X", "after_send"
                            )
        after = {
            **batch, "status": "EVALUATING", "numberOfTransactions": 0,
            "currentAmountCents": 0, "initialAmountCents": 6000,
        }
        with patch.object(reward_batch_counter_steps, "_batch_observation",
                          return_value=(after, [])):
            reward_batch_counter_steps.step_live_reward_batch_counters_match(
                self.context, "X"
            )
            reward_batch_counter_steps.step_reward_batch_keeps_initial_snapshot(
                self.context, "X", "after_send"
            )
        with (
            patch.object(reward_batch_counter_steps, "_batch_observation",
                         return_value=({**after, "initialAmountCents": 0}, [])),
            self.assertRaisesRegex(AssertionError, "initialAmountCents"),
        ):
            reward_batch_counter_steps.step_reward_batch_keeps_initial_snapshot(
                self.context, "X", "after_send"
            )

    def test_suspended_snapshot_capture_rejects_zero_and_preserves_valid_amount(self):
        rows = [{"trxId": "transaction", "rewardBatchTrxStatus": "SUSPENDED",
                 "rewardAmountCents": 6000}]
        batch = {
            "id": "source", "status": "EVALUATING",
            "numberOfTransactions": 1, "numberOfTransactionsElaborated": 1,
            "numberOfTransactionsSuspended": 1, "numberOfTransactionsRejected": 0,
            "currentAmountCents": 6000, "excludedAmountCents": 0,
            "approvedAmountCents": 0,
        }
        for suspended_amount in (0, 5000, 6000):
            with self.subTest(suspended_amount=suspended_amount):
                actual = {**batch, "suspendedAmountCents": suspended_amount}
                with (
                    patch.object(reward_batch_counter_steps, "_batch_observation",
                                 return_value=(actual, rows)),
                    patch.object(reward_batch_counter_steps.time, "sleep"),
                ):
                    if suspended_amount == 6000:
                        reward_batch_counter_steps.step_capture_reward_batch_counters(
                            self.context, "X", "before_approving"
                        )
                    else:
                        with self.assertRaisesRegex(AssertionError, "suspendedAmountCents"):
                            reward_batch_counter_steps.step_capture_reward_batch_counters(
                                self.context, "X", "before_approving"
                            )
        for status in ("APPROVING", "APPROVED"):
            with self.subTest(status=status):
                after = {
                    **batch, "status": status, "numberOfTransactions": 0,
                    "numberOfTransactionsElaborated": 0,
                    "numberOfTransactionsSuspended": 0, "currentAmountCents": 0,
                    "suspendedAmountCents": 6000,
                }
                with patch.object(reward_batch_counter_steps, "_batch_observation",
                                  return_value=(after, [])):
                    reward_batch_counter_steps.step_reward_batch_keeps_suspended_snapshot(
                        self.context, "X", "before_approving"
                    )
                    reward_batch_counter_steps.step_live_reward_batch_counters_match(
                        self.context, "X"
                    )
                with (
                    patch.object(reward_batch_counter_steps, "_batch_observation",
                                 return_value=({**after, "suspendedAmountCents": 0}, [])),
                    self.assertRaisesRegex(AssertionError, "suspendedAmountCents"),
                ):
                    reward_batch_counter_steps.step_reward_batch_keeps_suspended_snapshot(
                        self.context, "X", "before_approving"
                    )

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

    def test_operator_decision_notes_round_trip_without_changing_legacy_fields(self):
        payload = {
            'transactionIds': ['transaction'],
            'reason': 'Rejected by operator',
            'checksError': ChecksErrorDTO(price_error=True).to_dict(),
            'officialNote': 'Synthetic operator rejection: price check failed',
            'internalNote': 'Synthetic rejection for reward-batch counter testing',
        }
        request = TransactionActionRequest.from_dict(payload)
        self.assertEqual(request.to_dict(), payload)
        self.assertEqual(request.official_note, payload['officialNote'])
        self.assertEqual(request.internal_note, payload['internalNote'])
        legacy_payload = {
            key: value for key, value in payload.items()
            if key not in ('officialNote', 'internalNote')
        }
        self.assertEqual(
            TransactionActionRequest.from_dict(legacy_payload).to_dict(), legacy_payload
        )

    def test_operator_actions_serialize_required_decision_notes_at_transport_boundary(self):
        expected_decisions = {
            'reject': {
                'reason': 'Rejected by operator',
                'checksError': ChecksErrorDTO(price_error=True).to_dict(),
                'officialNote': 'Synthetic operator rejection: price check failed',
                'internalNote': 'Synthetic rejection for reward-batch counter testing',
            },
            'suspend': {
                'reason': 'Suspended by operator',
                'checksError': ChecksErrorDTO(generic_error=True).to_dict(),
                'officialNote': 'Synthetic operator suspension: generic check requires review',
                'internalNote': 'Synthetic suspension for reward-batch counter testing',
            },
        }
        for action in ('approve', 'reject', 'suspend'):
            with self.subTest(action=action):
                with patch.object(requests, 'post', return_value=response()) as post:
                    transaction_utilities.perform_reward_batch_transaction_action(
                        'initiative', 'source', 'test-operator-token', 'transaction', action
                    )
                post.assert_called_once()
                prepared = requests.Request(
                    'POST', 'https://offline.invalid', json=post.call_args.kwargs['json']
                ).prepare()
                payload = json.loads(prepared.body)
                self.assertEqual(payload, {
                    'transactionIds': ['transaction'],
                    **expected_decisions.get(action, {}),
                })

    def test_operator_action_http_failure_is_still_asserted(self):
        for action in ('reject', 'suspend'):
            with self.subTest(action=action):
                with (
                    patch.object(requests, 'post', return_value=response(status=400)),
                    self.assertRaisesRegex(AssertionError, f"'{action}' failed: 400"),
                ):
                    transaction_utilities.perform_reward_batch_transaction_action(
                        'initiative', 'source', 'test-operator-token', 'transaction', action
                    )

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
