from core.models import LockingAccount
from core.models import LockingGroup

from django.urls import reverse_lazy
from django.utils.http import urlencode


def get_locked_groups_ids():
    return {group.name: group.group.pk for group in LockingGroup.objects.all()}


def get_locked_account_ids():
    return {account.name: account.account.pk for account in LockingAccount.objects.all()}


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
