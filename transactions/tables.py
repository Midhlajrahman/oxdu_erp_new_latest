from core.base import BaseTable

from .models import Expense
from .models import Item
from .models import Transaction
from django_tables2 import columns


class ExpenseTable(BaseTable):
    created = None

    class Meta(BaseTable.Meta):
        model = Expense
        fields = ("bill_date", "expense_no", "party", "grand_total", "balance", "status")


class ItemTable(BaseTable):
    created = None

    class Meta(BaseTable.Meta):
        model = Item
        fields = ("name", "hsn_or_sac", "price", "tax_included", "price_with_out_tax", "tax")


class BaseTransactionTable(BaseTable):
    transaction_type = ""
    payment_method = ""
    action = columns.TemplateColumn(template_name="app/partials/table_actions2.html", orderable=False)

    class Meta(BaseTable.Meta):
        model = Transaction
        fields = ()

    def __init__(self, *args, **kwargs):
        if self.transaction_type == "RECEIPT":
            self.base_columns['opposite_account'].verbose_name = "Customer"
        elif self.transaction_type == "PAYMENT":
            self.base_columns['opposite_account'].verbose_name = "Supplier"
        super().__init__(*args, **kwargs)


class JournalVoucherTable(BaseTable):
    main_account = columns.Column(verbose_name="Debit Account")
    opposite_account = columns.Column(verbose_name="Credit Account")

    class Meta(BaseTable.Meta):
        model = Transaction
        fields = ("voucher_no", "main_account", "opposite_account", "date", "amount")


class CashReceiptTransactionTable(BaseTransactionTable):
    transaction_type = "RECEIPT"
    payment_method = "CASH"

    class Meta(BaseTransactionTable.Meta):
        fields = ("voucher_no", "date", "opposite_account", "amount")


class BankReceiptTransactionTable(BaseTransactionTable):
    transaction_type = "RECEIPT"
    payment_method = "BANK"
    main_account = columns.Column(verbose_name="Bank Account")

    class Meta(BaseTransactionTable.Meta):
        fields = ("voucher_no", "date", "main_account", "opposite_account", "amount")


class CashPaymentTransactionTable(BaseTransactionTable):
    transaction_type = "PAYMENT"
    payment_method = "CASH"

    class Meta(BaseTransactionTable.Meta):
        fields = ("voucher_no", "date", "opposite_account", "amount")


class BankPaymentTransactionTable(BaseTransactionTable):
    transaction_type = "PAYMENT"
    payment_method = "BANK"
    main_account = columns.Column(verbose_name="Bank Account")

    class Meta(BaseTransactionTable.Meta):
        fields = ("voucher_no", "date", "main_account", "opposite_account", "amount")
