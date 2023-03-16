import requests

from conf.configuration import settings


def timeline(initiative_id, token):
    """API to get timeline of a user
        :param initiative_id: ID of the initiative of interest.
        :param token: token IO.
        :returns: the response of the call.
        :rtype: requests.Response
    """
    return requests.get(
        f'{settings.base_path.IO}{settings.IDPAY.domain}{settings.IDPAY.endpoints.timeline}/{initiative_id}/?page=0&size=10',
        headers={
            "Authorization": f'Bearer {token}',
        },
        timeout=5000)
