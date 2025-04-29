from core.base import BaseAdmin

from .models import Account
from .models import GroupMaster
from django.contrib import admin


@admin.register(GroupMaster)
class GroupMasterAdmin(BaseAdmin):
    search_fields = ("name",)
    list_filter = ("nature_of_group", "main_group")


@admin.register(Account)
class AccountAdmin(BaseAdmin):
    search_fields = ("name",)
