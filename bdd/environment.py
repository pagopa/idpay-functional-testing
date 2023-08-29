import time

from api.idpay import delete_initiative
from conf.configuration import secrets
from conf.configuration import settings
from util.utility import create_initiative


def before_all(context):
    """Initialize initiatives' IDs map
    """
    secrets.initiatives = {}


def before_feature(context, feature):
    """Create the feature's initiative if it has not been yet created for this run
    """
    context.shared_data = {}
    # Create the initiative given a proper first tag on feature file (if not created in this run)
    context.curr_initiative_name = feature.tags[0]

    if context.curr_initiative_name not in secrets.initiatives.keys():
        secrets.initiatives[context.curr_initiative_name] = {}
        secrets.initiatives[context.curr_initiative_name]['id'] = create_initiative(
            initiative_name_in_settings=context.curr_initiative_name)
        print(
            f'Created initiative {secrets.initiatives[context.curr_initiative_name]["id"]} ({context.curr_initiative_name})')
        time.sleep(settings.INITIATIVE_STARTUP_TIME_SECONDS)


def after_all(context):
    """Delete each initiative created during the run
    """

    # Prevents the deletion of the fixed initiatives
    fixed_initiatives = []

    if not settings.KEEP_INITIATIVES_AFTER_TEST:
        for initiative_id in secrets.initiatives.values():
            if initiative_id not in fixed_initiatives:
                res = delete_initiative(initiative_id=initiative_id['id'])
                if res.status_code == 204:
                    print(
                        f'Deleted initiative {initiative_id["id"]}')
                else:
                    print(
                        f'Failed to delete initiative {initiative_id["id"]}')
