"""Parse configuration file to obtain current settings.
"""
from dynaconf import Dynaconf

IDPAY_ENV_VAR_PREFIX = 'IDPAY'

# `envvar_prefix` = export envvars with IDPAY_ENV_VAR_PREFIX as prefix.
# `settings_files` = Load settings files in the order.
settings = Dynaconf(
    envvar_prefix=IDPAY_ENV_VAR_PREFIX,
    settings_files=['settings.yaml'],
)

# Load the secrets for the specified environment
secrets = {}

all_secrets = Dynaconf(settings_files=settings.SECRET_PATH)
if settings.TARGET_ENV in all_secrets:
    secrets = all_secrets[settings.TARGET_ENV]
