from core.base import BaseTable

from .models import Account
from .models import GroupMaster


class GroupMasterTable(BaseTable):

    class Meta(BaseTable.Meta):
        model = GroupMaster
        fields = ("code", "name", "nature_of_group", "main_group")


class AccountTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Account
        fields = ("name", "under")


# class BankTransactionTable(BaseTable):
#     main_account = columns.Column(verbose_name="Bank Account")

#     class Meta(BaseTable.Meta):
#         model = Transaction
#         fields = ("date", "main_account", "cheque_no", "opposite_account", "amount")
#         attrs = {"class": "table mb-0 table-striped "}


# class CashTransactionTable(BaseTable):
#     main_account = columns.Column(verbose_name="Cash Account")

#     class Meta(BaseTable.Meta):
#         model = Transaction
#         fields = ("date", "main_account", "voucher_no", "opposite_account", "amount")
#         attrs = {"class": "table mb-0 table-striped "}


# class ExpenseTable(BaseTable):
#     created=None
#     class Meta(BaseTable.Meta):
#         model = Expense
#         fields = ("bill_date","expense_no","party","grand_total","balance","status")
#         attrs = {"class": "table mb-0 table-striped "}
