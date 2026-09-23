"""Optional WireMock observation for isolated RDB dependency tests.

This client observes real backend calls. It never fabricates RDB API responses.
"""
import requests

from conf.configuration import settings


def get_requests(base_url):
    return requests.get(f'{base_url.rstrip("/")}/__admin/requests', timeout=settings.default_timeout)


def add_mapping(base_url, mapping):
    return requests.post(f'{base_url.rstrip("/")}/__admin/mappings',
                         json=mapping, timeout=settings.default_timeout)


def delete_mapping(base_url, mapping_id):
    return requests.delete(f'{base_url.rstrip("/")}/__admin/mappings/{mapping_id}',
                           timeout=settings.default_timeout)
