"""Parse configuration file to obtain current settings.
"""
from collections.abc import Mapping

from dynaconf import Dynaconf

PARI_ENV_VAR_PREFIX = 'PARI'

# `envvar_prefix` = export envvars with IDPAY_ENV_VAR_PREFIX as prefix.
# `settings_files` = Load settings files in the order.
settings = Dynaconf(
    envvar_prefix=PARI_ENV_VAR_PREFIX,
    settings_files=['settings.yaml'],
)

# Load only the explicitly selected environment; never fall back to empty secrets.
all_secrets = Dynaconf(settings_files=settings.SECRET_PATH)

if settings.TARGET_ENV not in all_secrets:
    raise ValueError(
        f"Missing environment '{settings.TARGET_ENV}' in {settings.SECRET_PATH}. "
        "Set PARI_TARGET_ENV to the intended environment and PARI_SECRET_PATH "
        "to its configuration file. No tests have been started."
    )
secrets = all_secrets[settings.TARGET_ENV]
if not isinstance(secrets, Mapping) or not secrets:
    raise ValueError(
        f"Environment '{settings.TARGET_ENV}' in {settings.SECRET_PATH} "
        "must contain a nonempty configuration object."
    )
