import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import uuid

from django.urls import reverse_lazy
from django.utils.http import urlencode

def build_url(viewname, kwargs=None, query_params=None):
    """
    Helper function to build a URL with optional path parameters and query parameters.

    :param viewname: Name of the view for reverse URL resolution.
    :param kwargs: Dictionary of path parameters.
    :param query_params: Dictionary of query parameters.
    :return: Constructed URL with query parameters.
    """
    url = reverse_lazy(viewname, kwargs=kwargs or {})
    if query_params:
        url = f"{url}?{urlencode(query_params)}"
    return url


def remove_bg(image_path):
    api_key = "v1nasmu4ViyDFom4NP4Pixur"
    with open(image_path, 'rb') as file:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': file},
            data={'size': 'auto'},
            headers={'X-Api-Key': api_key}
        )

    if response.status_code == 200:
        filename = f"temp/removed_bg_{uuid.uuid4().hex}.png"
        return default_storage.save(filename, ContentFile(response.content))
    else:
        raise Exception(f"Remove.bg API error: {response.status_code} - {response.text}")