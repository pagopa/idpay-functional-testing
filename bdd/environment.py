from api.idpay import delete_initiative
from conf.configuration import secrets
from conf.configuration import settings
from util.utility import create_initiative_and_update_conf


def before_all(context):
    """Initialize initiatives' IDs map
    """
    secrets['newly_created'] = set()


def before_feature(context, feature):
    """Create the feature's initiative if it has not been yet created for this run
    """

    # Create an initiative for each proper tag on feature file (if not created yet in this run)
    if not secrets.initiatives:
        secrets.initiatives = {}
    for curr_initiative_name in feature.tags:
        if curr_initiative_name in settings.initiatives:
            if curr_initiative_name not in secrets.initiatives.keys():
                secrets.initiatives[curr_initiative_name] = {}
                create_initiative_and_update_conf(initiative_name=curr_initiative_name)


def after_all(context):
    """Delete each initiative created during the run
    """

    if not settings.KEEP_INITIATIVES_AFTER_TEST:
        for initiative_id in secrets['newly_created']:
            res = delete_initiative(initiative_id=initiative_id)
            if res.status_code == 204:
                print(
                    f'Deleted initiative {initiative_id}')
            else:
                print(
                    f'Failed to delete initiative {initiative_id}')
