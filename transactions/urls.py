from . import views
from django.urls import path


app_name = "transactions"

urlpatterns = [
    path("get_item_details", views.get_item_details, name="get_item_details"),
    path("get_references", views.get_references, name="get_references"),
    # item
    path("item/list/", views.ItemListView.as_view(), name="item_list"),
    path("item/<str:pk>/detail/", views.ItemDetailView.as_view(), name="item_detail"),
    path("item/create/", views.ItemCreateView.as_view(), name="item_create"),
    path("item/<str:pk>/update/", views.ItemUpdateView.as_view(), name="item_update"),
    path("item/<str:pk>/delete/", views.ItemDeleteView.as_view(), name="item_delete"),
    # Expense
    path("expenses/", views.ExpenseListView.as_view(), name="expense_list"),
    path("expense/<str:pk>/", views.ExpenseDetailView.as_view(), name="expense_detail"),
    path("new/expense/", views.ExpenseCreateView.as_view(), name="expense_create"),
    path("expense/<str:pk>/update/", views.ExpenseUpdateView.as_view(), name="expense_update"),
    path("expense/<str:pk>/delete/", views.ExpenseDeleteView.as_view(), name="expense_delete"),
    # transaction list
    path("cash_receipts/", views.CashReceiptListView.as_view(), name="cash_receipt_list"),
    path("bank_receipts/", views.BankReceiptListView.as_view(), name="bank_receipt_list"),
    path("cash_payments/", views.CashPaymentListView.as_view(), name="cash_payment_list"),
    path("bank_payments/", views.BankPaymentListView.as_view(), name="bank_payment_list"),
    # transaction create
    path("cash_receipts/create/", views.CashReceiptCreateView.as_view(), name="cash_receipt_create"),
    path("bank_receipts/create/", views.BankReceiptCreateView.as_view(), name="bank_receipt_create"),
    path("cash_payments/create/", views.CashPaymentCreateView.as_view(), name="cash_payment_create"),
    path("bank_payments/create/", views.BankPaymentCreateView.as_view(), name="bank_payment_create"),
    # transaction update
    path("cash_receipt/<str:pk>/update/", views.CashReceiptUpdateView.as_view(), name="cash_receipt_update"),
    path("bank_receipt/<str:pk>/update/", views.BankReceiptUpdateView.as_view(), name="bank_receipt_update"),
    path("cash_payment/<str:pk>/update/", views.CashPaymentUpdateView.as_view(), name="cash_payment_update"),
    path("bank_payment/<str:pk>/update/", views.BankPaymentUpdateView.as_view(), name="bank_payment_update"),
    path("transaction/<str:pk>/", views.TransactionDetailView.as_view(), name="transaction_detail"),
    path("transaction/<str:pk>/delete/", views.TrsansactionDeleteView.as_view(), name="transaction_delete"),
    # jv
    path("journal_vouchers/", views.JournalVoucherListView.as_view(), name="journal_voucher_list"),
    path("journal_voucher/create/", views.JournalVoucherCreateView.as_view(), name="journal_voucher_create"),
    path("journal_voucher/<str:pk>/update/", views.JournalVoucherUpdateView.as_view(), name="journal_voucher_update"),
]
