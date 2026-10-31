"""Offline counter-oracle checks, independent of integration fixtures and secrets."""
import unittest

from util.reward_batch_counters import derive_live_counters
from util.reward_batch_counters import derive_state_dependent_live_counters
from util.reward_batch_counters import derive_visible_live_counters
from util.reward_batch_counters import transaction_batch_status
from util.reward_batch_counters import transaction_reward_amount


MIXED_TRANSACTIONS = [
    {'rewardBatchTrxStatus': 'TO_CHECK', 'rewardAmountCents': 11},
    {'rewardBatchTrxStatus': 'CONSULTABLE', 'rewardAmountCents': 23},
    {'rewardBatchTrxStatus': 'approved', 'accruedRewardCents': 37},
    {'rewardBatchTrxStatus': 'SUSPENDED', 'rewardAmountCents': 41},
    {'rewardBatchTrxStatus': 'suspended', 'rewardAmountCents': 43},
    {'rewardBatchTrxStatus': 'REJECTED', 'rewardAmountCents': 53},
    {'rewardBatchTrxStatus': 'rejected', 'rewardAmountCents': 59},
    {'rewardBatchTrxStatus': 'UNKNOWN', 'rewardAmountCents': 61},
    {'rewardAmountCents': 67},
    {'rewardBatchTrxStatus': None, 'rewardAmountCents': 71},
]


class RewardBatchCountersTest(unittest.TestCase):
    def test_reward_field_preference_and_fallback(self):
        cases = [
            ({'rewardAmountCents': 137, 'accruedRewardCents': 999}, 137),
            ({'rewardAmountCents': 0, 'accruedRewardCents': 999}, 0),
            ({'rewardAmountCents': '137', 'accruedRewardCents': '999'}, 137),
            ({'rewardAmountCents': 137}, 137),
            ({'accruedRewardCents': 137}, 137),
            ({'rewardAmountCents': None, 'accruedRewardCents': 137}, 137),
            ({'accruedRewardCents': 0}, 0),
            ({'rewardAmountCents': None, 'accruedRewardCents': '137'}, 137),
            ({'rewardAmountCents': '0', 'accruedRewardCents': 137}, 0),
        ]
        for transaction, expected in cases:
            with self.subTest(transaction=transaction):
                self.assertEqual(transaction_reward_amount(transaction), expected)

    def test_missing_reward_error_does_not_disclose_transaction_data(self):
        cases = [
            {},
            {'rewardAmountCents': None},
            {'accruedRewardCents': None},
            {'rewardAmountCents': None, 'accruedRewardCents': None},
        ]
        identity = {
            'transactionId': 'private-test-transaction',
            'fiscalCode': 'private-test-citizen',
            'token': 'private-test-token',
        }
        for fields in cases:
            with self.subTest(fields=fields):
                with self.assertRaises(AssertionError) as raised:
                    transaction_reward_amount({**fields, **identity})
                self.assertEqual(
                    str(raised.exception),
                    'Transaction does not expose a reward amount; missing fields: '
                    'rewardAmountCents, accruedRewardCents',
                )
                for value in identity.values():
                    self.assertNotIn(value, str(raised.exception))

    def test_counter_derivations_reject_rows_without_reward_amounts(self):
        derivations = [
            derive_live_counters,
            lambda rows: derive_state_dependent_live_counters('CREATED', rows),
            lambda rows: derive_state_dependent_live_counters('SENT', rows),
            lambda rows: derive_visible_live_counters('APPROVED', rows),
        ]
        rows = [
            {'rewardBatchTrxStatus': 'APPROVED', 'rewardAmountCents': 137},
            {'rewardBatchTrxStatus': 'UNKNOWN', 'transactionId': 'private-test-id'},
        ]
        for index, derive in enumerate(derivations):
            with self.subTest(derivation=index):
                with self.assertRaises(AssertionError) as raised:
                    derive(rows)
                self.assertEqual(
                    str(raised.exception),
                    'Transaction does not expose a reward amount; missing fields: '
                    'rewardAmountCents, accruedRewardCents',
                )

    def test_transaction_status_normalization(self):
        cases = [
            ({'rewardBatchTrxStatus': 'APPROVED'}, 'APPROVED'),
            ({'rewardBatchTrxStatus': 'approved'}, 'APPROVED'),
            ({'rewardBatchTrxStatus': 'SuSpEnDeD'}, 'SUSPENDED'),
            ({'rewardBatchTrxStatus': 'unknown'}, 'UNKNOWN'),
            ({'rewardBatchTrxStatus': ''}, ''),
            ({'rewardBatchTrxStatus': None}, None),
            ({}, None),
        ]
        for transaction, expected in cases:
            with self.subTest(transaction=transaction):
                self.assertEqual(transaction_batch_status(transaction), expected)

    def test_each_transaction_status_maps_to_the_expected_counters(self):
        cases = [
            ('TO_CHECK', 0, 0, 0, 137, 0, 0),
            ('CONSULTABLE', 0, 0, 0, 137, 0, 0),
            ('APPROVED', 1, 0, 0, 137, 0, 0),
            ('SUSPENDED', 1, 1, 0, 0, 0, 137),
            ('REJECTED', 1, 0, 1, 0, 137, 0),
            ('UNKNOWN', 0, 0, 0, 0, 0, 0),
            ('', 0, 0, 0, 0, 0, 0),
            (None, 0, 0, 0, 0, 0, 0),
        ]
        for (
            status,
            elaborated,
            suspended,
            rejected,
            approved,
            excluded,
            suspended_amount,
        ) in cases:
            with self.subTest(status=status):
                transaction = {
                    'rewardBatchTrxStatus': status,
                    'rewardAmountCents': 137,
                }
                self.assertEqual(
                    derive_visible_live_counters('EVALUATING', [transaction]),
                    {
                        'numberOfTransactions': 1,
                        'numberOfTransactionsElaborated': elaborated,
                        'numberOfTransactionsSuspended': suspended,
                        'numberOfTransactionsRejected': rejected,
                        'currentAmountCents': 137,
                        'excludedAmountCents': excluded,
                        'approvedAmountCents': approved,
                        'suspendedAmountCents': suspended_amount,
                    },
                )

    def test_mixed_rows_include_unknown_and_missing_statuses_in_totals(self):
        self.assertEqual(
            derive_live_counters(MIXED_TRANSACTIONS),
            {
                'numberOfTransactions': 10,
                'numberOfTransactionsElaborated': 5,
                'numberOfTransactionsSuspended': 2,
                'numberOfTransactionsRejected': 2,
                'currentAmountCents': 466,
                'excludedAmountCents': 112,
            },
        )

    def test_state_dependent_keys_and_amounts(self):
        cases = [
            (
                'CREATED',
                {
                    'approvedAmountCents': 0,
                    'initialAmountCents': 466,
                    'suspendedAmountCents': 84,
                },
            ),
            ('SENT', {'approvedAmountCents': 0, 'suspendedAmountCents': 84}),
            ('EVALUATING', {'approvedAmountCents': 71, 'suspendedAmountCents': 84}),
            ('APPROVING', {'approvedAmountCents': 71}),
            ('APPROVED', {'approvedAmountCents': 71}),
        ]
        for status, expected in cases:
            for spelling in (status, status.lower()):
                with self.subTest(status=spelling):
                    self.assertEqual(
                        derive_state_dependent_live_counters(
                            spelling, MIXED_TRANSACTIONS
                        ),
                        expected,
                    )

    def test_visible_counters_include_live_totals_but_omit_snapshots(self):
        live_expected = {
            'numberOfTransactions': 10,
            'numberOfTransactionsElaborated': 5,
            'numberOfTransactionsSuspended': 2,
            'numberOfTransactionsRejected': 2,
            'currentAmountCents': 466,
            'excludedAmountCents': 112,
        }
        cases = [
            (
                'CREATED',
                {
                    'approvedAmountCents': 0,
                    'initialAmountCents': 466,
                    'suspendedAmountCents': 84,
                },
            ),
            ('SENT', {'approvedAmountCents': 0, 'suspendedAmountCents': 84}),
            ('EVALUATING', {'approvedAmountCents': 71, 'suspendedAmountCents': 84}),
            ('APPROVING', {'approvedAmountCents': 71}),
            ('APPROVED', {'approvedAmountCents': 71}),
        ]
        for status, state_expected in cases:
            with self.subTest(status=status):
                self.assertEqual(
                    derive_visible_live_counters(status, MIXED_TRANSACTIONS),
                    {**live_expected, **state_expected},
                )

    def test_empty_rows_have_zero_live_counters_and_state_specific_keys(self):
        live_expected = {
            'numberOfTransactions': 0,
            'numberOfTransactionsElaborated': 0,
            'numberOfTransactionsSuspended': 0,
            'numberOfTransactionsRejected': 0,
            'currentAmountCents': 0,
            'excludedAmountCents': 0,
        }
        cases = [
            (
                'CREATED',
                {
                    'approvedAmountCents': 0,
                    'initialAmountCents': 0,
                    'suspendedAmountCents': 0,
                },
            ),
            ('SENT', {'approvedAmountCents': 0, 'suspendedAmountCents': 0}),
            ('EVALUATING', {'approvedAmountCents': 0, 'suspendedAmountCents': 0}),
            ('APPROVING', {'approvedAmountCents': 0}),
            ('APPROVED', {'approvedAmountCents': 0}),
        ]
        self.assertEqual(derive_live_counters([]), live_expected)
        for status, state_expected in cases:
            with self.subTest(status=status):
                self.assertEqual(
                    derive_state_dependent_live_counters(status, []),
                    state_expected,
                )
                self.assertEqual(
                    derive_visible_live_counters(status, []),
                    {**live_expected, **state_expected},
                )


if __name__ == '__main__':
    unittest.main()
