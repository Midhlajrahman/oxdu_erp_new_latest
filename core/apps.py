from django.apps import AppConfig
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError
from django.core.exceptions import ImproperlyConfigured

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        try:
            from django.db import connection
            if not connection.introspection.table_names():
                raise ImproperlyConfigured("Database is not ready yet.")

            from .models import LockingAccount, LockingGroup
            settings.LOCKED_GROUPS_IDS = {group.name: group.group.pk for group in LockingGroup.objects.all()}
            settings.LOCKED_ACCOUNT_IDS = {account.name: account.account.pk for account in LockingAccount.objects.all()}
        except (OperationalError, ProgrammingError, ImproperlyConfigured) as e:
            settings.LOCKED_GROUPS_IDS = {}
            settings.LOCKED_ACCOUNT_IDS = {}
            print(f"Database error encountered: {e}")
