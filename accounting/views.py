from accounting.models import Account
from accounting.models import GroupMaster
from core import mixins

from . import tables
from .forms import AccountForm


class GroupMasterListView(mixins.HybridListView):
    model = GroupMaster
    table_class = tables.GroupMasterTable
    filterset_fields = {"name": ["icontains"], "nature_of_group": ['exact'], "main_group": ['exact']}
    search_fields = ("name", "code", "nature_of_group", "main_group")
    branch_filter = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_master"] = True
        return context


class GroupMasterDetailView(mixins.HybridDetailView):
    model = GroupMaster


class GroupMasterCreateView(mixins.HybridCreateView):
    model = GroupMaster
    exclude = ("creator", "parent", "is_locked")


class GroupMasterUpdateView(mixins.HybridUpdateView):
    model = GroupMaster
    exclude = ("creator", "parent", "is_locked")


class GroupMasterDeleteView(mixins.HybridDeleteView):
    model = GroupMaster


class AccountListView(mixins.HybridListView):
    model = Account
    table_class = tables.AccountTable
    filterset_fields = {"name": ["icontains"], "under": ['exact']}
    serach_fields = ("name", "under__name")
    branch_filter = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_master"] = True
        return context


class AccountDetailView(mixins.HybridDetailView):
    model = Account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_change'] = False
        context['can_delete'] = False
        return context


class AccountCreateView(mixins.HybridCreateView):
    model = Account
    exclude = None
    form_class = AccountForm
    template_name = "accounting/account_form.html"


class AccountUpdateView(mixins.HybridUpdateView):
    model = Account
    exclude = None
    form_class = AccountForm
    template_name = "accounting/account_form.html"


class AccountDeleteView(mixins.HybridDeleteView):
    model = Account
