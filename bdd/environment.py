from api.idpay import delete_initiative
from conf.configuration import secrets
from conf.configuration import settings
from util.utility import create_initiative


def before_feature(context, feature):
    context.shared_data = {}
    # Create the initiative given a proper first tag on feature file
    context.curr_initiative_name = feature.tags[0]
    secrets.initiatives[context.curr_initiative_name] = {}
    secrets.initiatives[context.curr_initiative_name]['id'] = create_initiative(
        initiative_name_in_settings=context.curr_initiative_name)
    print(
        f'Created initiative {secrets.initiatives[context.curr_initiative_name]["id"]} ({context.curr_initiative_name})')


def after_scenario(context, scenario):
    # Save the current initiative id at feature context level
    context.shared_data['curr_initiative_id'] = context.initiative_id


def after_feature(context, feature):
    # Prevents the deletion of the fixed initiatives
    fixed_initiatives = []
    curr_initiative_id = context.shared_data['curr_initiative_id']

    # Avoid deletion if at least one scenario failed
    if settings.KEEP_INITIATIVES_ON_FAIL and any(scenario.status == 'failed' for scenario in feature.scenarios):
        print('At least one scenario within this feature failed. Skipping additional actions.')
        return

    if not settings.KEEP_INITIATIVES_AFTER_TEST and curr_initiative_id not in fixed_initiatives:
        res = delete_initiative(initiative_id=context.shared_data['curr_initiative_id'])
        if res.status_code == 204:
            print(f'Deleted initiative {context.shared_data["curr_initiative_id"]} ({context.curr_initiative_name})')
        else:
            print(
                f'Failed to delete initiative {context.shared_data["curr_initiative_id"]} ({context.curr_initiative_name})')
