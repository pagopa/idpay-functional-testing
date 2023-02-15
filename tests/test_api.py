from api.endpoints import get_uuid


def test_get_uuid():
    response = get_uuid()
    assert len(response.json()['uuid']) == 36
    assert response.status_code == 200
