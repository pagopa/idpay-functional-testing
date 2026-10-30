# Project instructions

This Python 3.14 BDD suite tests the PARI platform. Active features live in
`bdd/features/common_bonus_features`, `bdd/features/bonus_elettrodomestici` and
`bdd/features/bonus_decoder`. Reusable Behave steps live in `bdd/steps`.

Install locked dependencies with `pipenv sync`. CI runs BDD through
`.github/workflows/test-run.yaml` and retrieves secrets from Azure Key Vault.
Use the placeholder-only `conf/pari-feature-secrets-template.json` to configure
an ignored local file, or select one through `PARI_SECRET_PATH`.
`PARI_TARGET_ENV` selects the environment. Never commit credentials, tokens,
private keys, environment identities or generated reports.

See README.md for offline unit tests, BDD dry runs and documentation builds.
`tests/unit` uses unittest and mocks HTTP calls. Remote BDD runs require the
configured environment and its credentials. Preserve polling, scenario cleanup,
initiative selection and failure-preservation controls. Do not run tests
concurrently against shared initiatives.

`api/` contains HTTP requests; `util/` contains reusable flows and data generation.
Keep endpoints in `settings.yaml`, environment values in secrets, and scenario
state on Behave's `context`. Tags filter scenarios; execution inputs choose the
initiative, as described in README.md. Generated documentation is ignored.

Run `pre-commit run --all-files` for configured repository checks.
Keep `Pipfile`, `Pipfile.lock` and `requirements.txt` consistent when changing dependencies.
