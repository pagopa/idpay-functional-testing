import logging
import os

from behave.tag_expression import make_tag_expression
from behave.tag_expression.v1 import TagExpression
from cucumber_tag_expressions.model import And
from cucumber_tag_expressions.model import Literal
from cucumber_tag_expressions.model import Not
from cucumber_tag_expressions.model import Or

from conf.configuration import secrets
from conf.configuration import settings
from util.transaction_utilities import cleanup_reward_batches_and_related_transactions
from util.utility import create_initiative_and_update_conf


INITIATIVE_CONFIGS = {
    "common_bonus_features": {
        "initiative_id": "common_bonus_features",
        "product_gtin": "TUMBLEDRYERS03",
    },
    "bonus_decoder": {
        "initiative_id": "bonus_decoder",
        "product_gtin": "DECODER20",
    },
}
DEFAULT_INITIATIVE = "common_bonus_features"
logger = logging.getLogger(__name__)


def positive_initiative_tags(expression, negated=False):
    if isinstance(expression, TagExpression):
        return {
            tag for terms in expression.ands for tag in terms
            if tag in INITIATIVE_CONFIGS
        }
    if isinstance(expression, Literal):
        name = expression.name.lstrip("@")
        return {name} if not negated and name in INITIATIVE_CONFIGS else set()
    if isinstance(expression, Not):
        return positive_initiative_tags(expression.term, not negated)
    if isinstance(expression, (And, Or)):
        result = set()
        for term in expression.terms:
            result.update(positive_initiative_tags(term, negated))
        return result
    return set()


def select_initiative(context):
    """Select from execution arguments, never from feature/scenario tags."""
    config = getattr(context, "config", None)
    cli_tags = positive_initiative_tags(
        make_tag_expression(getattr(config, "tags", []) or [])
    )
    environment_tag = (
        os.environ.get("PARI_FEATURE_TAG") or os.environ.get("FEATURE_TAG", "")
    ).strip().lstrip("@")
    if len(cli_tags) == 1:
        return next(iter(cli_tags))
    if len(cli_tags) > 1:
        if environment_tag in cli_tags:
            return environment_tag
        raise ValueError(
            "Execution selects multiple initiatives; set PARI_FEATURE_TAG "
            "or FEATURE_TAG to one of: " + ", ".join(sorted(cli_tags))
        )
    if environment_tag in INITIATIVE_CONFIGS:
        return environment_tag
    if environment_tag and environment_tag != "all":
        logger.warning(
            "Unknown initiative tag '%s'; using '%s'",
            environment_tag,
            DEFAULT_INITIATIVE,
        )
    return DEFAULT_INITIATIVE


def before_all(context):
    """Initialize initiatives' IDs map
    """
    secrets['newly_created'] = set()
    if 'organization_id' not in secrets and 'selfcare_info' in secrets:
        secrets['organization_id'] = secrets['selfcare_info']['test_institution']['orgId']


def before_feature(context, feature):
    """Create the feature's initiative if it has not been yet created for this run
    """
    context.reward_batches_to_cleanup = set()
    context.feature_initiative_names = set()

    # Bonus tags filter features; execution inputs select the Bonus to provision.
    if not secrets.get('initiatives'):
        secrets['initiatives'] = {}
    initiative_names = set(feature.tags).difference(INITIATIVE_CONFIGS)
    if set(feature.tags).intersection(INITIATIVE_CONFIGS):
        initiative_names.add(select_initiative(context))
    for curr_initiative_name in initiative_names:
        if curr_initiative_name in settings.initiatives:
            context.feature_initiative_names.add(curr_initiative_name)
            if curr_initiative_name not in secrets['initiatives']:
                secrets['initiatives'][curr_initiative_name] = {}
                create_initiative_and_update_conf(initiative_name=curr_initiative_name)


def before_scenario(context, scenario):
    """Select scenario configuration without mutating the shared defaults."""
    initiative_name = select_initiative(context)
    context.initiative_config = INITIATIVE_CONFIGS[initiative_name].copy()
    context.product_gtin = context.initiative_config["product_gtin"]

    context.initiative_id = secrets.get("initiatives", {}).get(
        context.initiative_config["initiative_id"], {}
    ).get("id", context.initiative_config["initiative_id"])

def after_feature(context, feature):
    if settings.REWARD_BATCH_CLEANUP and 'reward_batch' in feature.tags:
        for initiative_id, merchant_id, reward_batch_id in context.reward_batches_to_cleanup:
            print(
                "Cleaning up reward batch and related transactions for "
                f"reward_batch_id={reward_batch_id}, initiative_id={initiative_id}, "
                f"merchant_id={merchant_id}"
            )
            cleanup_reward_batches_and_related_transactions(
                merchant_id=merchant_id,
                initiative_id=initiative_id,
                reward_batch_id=reward_batch_id,
            )
