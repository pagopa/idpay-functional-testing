from conf.configuration import secrets
from conf.configuration import settings
from util.utility import create_initiative_and_update_conf
from util.utility import delete_new_initiatives_after_test


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
    delete_new_initiatives_after_test()


def after_feature(context, feature):
    """Delete the feature's initiative only if no scenario in the feature failed
    """
    if settings.KEEP_INITIATIVES_AFTER_FAILED_TEST:
        if any(scenario.status == 'failed' for scenario in feature.scenarios):
            for curr_initiative_name in feature.tags:
                if curr_initiative_name in secrets.initiatives.keys():
                    print(f'Tengo {curr_initiative_name}')
                    secrets['newly_created'].remove(secrets.initiatives[curr_initiative_name]['id'])
