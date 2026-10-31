# Reward batch counter tests

This suite verifies reward-batch counters across lifecycle operations.

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

Offline counter-oracle checks (no environment configuration required):

```shell
pipenv run python -m unittest discover -s tests/unit -p test_reward_batch_counters.py -v
```

Offline unit suite, including mocked API-token, month-rollover, and reassignment
cleanup checks:

```shell
PARI_SECRET_PATH=conf/pari-feature-secrets-template.json PARI_TARGET_ENV='<ENV>' \
  pipenv run python -m unittest discover -s tests/unit -v
```

The template's environment section is literally named `<ENV>`. These checks
do not provision initiatives or call the remote platform.

End-to-end counter scenarios require configured UAT credentials and create
remote test data. Keep cleanup enabled so both source and destination reward
batches are removed:

```shell
PARI_TARGET_ENV=uat PARI_REWARD_BATCH_CLEANUP=true \
  pipenv run behave --tags @reward_batch_counter
```

As described in the repository README, run the official end-to-end suite from
the GitHub Actions `test-run` workflow by selecting the `bdd` test type and the
`reward_batch_counter` tag. This runs all `CREATED`, `SENT`, `EVALUATING`, and
`APPROVING` cases together.
