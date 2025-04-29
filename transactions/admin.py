from core.base import BaseAdmin

from .models import Item
from .models import Transaction
from .models import TransactionItem
from django.contrib import admin


@admin.register(Item)
class ItemAdmin(BaseAdmin):
    pass


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0


@admin.register(Transaction)
class TransactionAdmin(BaseAdmin):
    inlines = [TransactionItemInline]
