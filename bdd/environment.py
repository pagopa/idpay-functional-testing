import time

from api.idpay import delete_initiative
from conf.configuration import secrets
from conf.configuration import settings
from util.utility import create_initiative


def before_all(context):
    """Initialize initiatives' IDs map
    """
    secrets['newly_created'] = set()


def before_feature(context, feature):
    """Create the feature's initiative if it has not been yet created for this run
    """
    created = False
    # Create an initiative for each proper tag on feature file (if not created yet in this run)
    if not secrets.initiatives:
        secrets.initiatives = {}
    for curr_initiative_name in feature.tags:
        if curr_initiative_name in settings.initiatives:
            if curr_initiative_name not in secrets.initiatives.keys():
                secrets.initiatives[curr_initiative_name] = {}
                secrets.initiatives[curr_initiative_name]['id'] = create_initiative(
                    initiative_name_in_settings=curr_initiative_name)
                print(
                    f'Created initiative {secrets.initiatives[curr_initiative_name]["id"]} ({curr_initiative_name})')
                secrets['newly_created'].add(secrets.initiatives[curr_initiative_name]['id'])
                created = True

    if created:
        time.sleep(settings.INITIATIVE_STARTUP_TIME_SECONDS)


def after_all(context):
    """Delete each initiative created during the run
    """

    # Prevents the deletion of the fixed initiatives
    fixed_initiatives = set((x['id'] for x in secrets.initiatives.values())) - secrets.newly_created

    if not settings.KEEP_INITIATIVES_AFTER_TEST:
        for initiative in secrets.initiatives.values():
            if initiative['id'] not in fixed_initiatives:
                res = delete_initiative(initiative_id=initiative['id'])
                if res.status_code == 204:
                    print(
                        f'Deleted initiative {initiative["id"]}')
                else:
                    print(
                        f'Failed to delete initiative {initiative["id"]}')
