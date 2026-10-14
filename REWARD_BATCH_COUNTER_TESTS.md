# Reward batch counter tests

This suite verifies counters through a single end-to-end flow.

## How to read the Gherkin scenarios

- `Given` sets up the initial data.
- `When` performs the action under test.
- `Then` checks the observable result.
- `And` continues the preceding block.

The checks are integrated into existing scenarios in `reward_batch.feature`
when the business flow is already covered. The
`reward_batch_counters.feature` file contains only additional cases. The added
steps are implemented in `bdd/steps/reward_batch_counter_steps.py`.

## What is verified

- In `CREATED`, counters reflect the current transactions: a reversal removes a
  transaction from the totals, and postponement moves the same live
  contribution to the following month's batch.
- When a batch moves to `SENT`, `initialAmountCents` remains the snapshot
  captured when it was sent.
- In `APPROVING`, `suspendedAmountCents` remains the snapshot captured before
  suspended transactions are reassigned.
- The count and amount of `REJECTED` transactions remain live; they do not have
  a dedicated snapshot.

## Running the tests

End-to-end counter scenarios:

```shell
behave --tags @reward_batch_counter
```

As described in the repository README, run the official end-to-end suite from
the GitHub Actions `test-run` workflow by selecting the `bdd` test type and the
`reward_batch_counter` tag. This runs all `CREATED`, `SENT`, `EVALUATING`, and
`APPROVING` cases together.
