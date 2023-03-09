import requests


def accept_terms_and_condition(url, token, initiative_id):
    """API to obtain an IO like token from a stub
        :param url: loginUrl
        :param token: token IO
        :param initiative_id: initiative on which onboard the user
        :returns:  The response of the call.
        :rtype: requests.Response
    """
    return requests.put(url,
                        headers={
                            'Content-Type': 'application/json',
                            "Authorization": f'Bearer {token}',
                        },
                        json={'initiativeId': initiative_id},
                        timeout=5000)
