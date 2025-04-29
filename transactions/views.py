from accounting.forms import AccountForm
from core import mixins
from core.models import Setting
from invoices.models import Invoice

from . import forms
from . import tables
from .forms import ExpenseForm
from .forms import ExpenseItemFormSet
from .forms import ItemForm
from .models import Expense
from .models import Item
from .models import Transaction
from django.conf import settings
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


LOCKED_GROUPS_ID = getattr(settings, 'LOCKED_GROUPS_IDS', [])
LOCKED_ACCOUNTS_ID = getattr(settings, 'LOCKED_ACCOUNT_IDS', [])


def get_references(request):
    branch_id = request.session.get('branch')
    academic_year_id = request.session.get('academic_year')
    customer_id = request.GET.get('customer_id')
    transaction_type = request.GET.get('transaction_type')

    if not customer_id or not transaction_type:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    if transaction_type == 'RECEIPT':
        references = Invoice.objects.filter(is_active=True, stage='invoice', customer_id=customer_id, branch_id=branch_id, academic_year_id=academic_year_id)
        # Filter objects where the `pending()` function returns a value greater than 0
        references = [invoice for invoice in references if invoice.pending() > 0]
        data = [
            {
                'id': ref.id,
                'str': str(ref),
                'date': ref.date.strftime('%d/%m/%Y') if ref.date else None,
                'pending': ref.pending(),
                'tds': ref.tds_amount,
                'discount': ref.discount_amount,
            }
            for ref in references
        ]
    else:
        references = Purchase.objects.filter(is_active=True, supplier_id=customer_id, sale_invoice__branch_id=branch_id, sale_invoice__academic_year_id=academic_year_id)
        references = [purchase for purchase in references if purchase.pending() > 0]
        data = [
            {'id': ref.id, 'str': str(ref), 'date': ref.bill_date.strftime('%d/%m/%Y') if ref.bill_date else None, 'pending': ref.pending(), 'tds': ref.tds, 'discount': 0}
            for ref in references
        ]

    return JsonResponse({'references': data})


def get_item_details(request):
    try:
        item_id = request.GET.get("itemId")
        item = get_object_or_404(Item, pk=item_id)

        price = item.price_with_out_tax

        # Retrieve tax information
        tax = item.tax

    except Exception:
        # Handle cases where the item doesn't exist or any unexpected error
        price = 0

    response = {"success": True, "result": {"price": price, "tax": tax}}
    return JsonResponse(response)


class ExpenseListView(mixins.HybridListView):
    model = Expense
    filterset_fields = {"bill_date": ['lte', 'gte']}
    table_class = tables.ExpenseTable
    serach_fields = ("expense_category__name", "expense_no", "party__name", "status")
    # template_name = "accounting/expense_filter.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_expense"] = True
        return context


class ExpenseDetailView(mixins.HybridDetailView):
    model = Expense


class ExpenseCreateView(mixins.HybridCreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "transactions/expense_form.html"
    exclude = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_form'] = ItemForm(self.request.POST or None)
        context['expense_category_form'] = AccountForm(locked_group_id=LOCKED_GROUPS_ID['INDIRECT_EXPENSE'])
        context['supplier_form'] = AccountForm(locked_group_id=LOCKED_GROUPS_ID['SUNDRY_CREDITORS'])
        context['expense_item_formset'] = ExpenseItemFormSet(self.request.POST or None, prefix='expense_item')
        return context

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['party'].queryset = form.fields['party'].queryset.filter(under__id__in=[LOCKED_GROUPS_ID['SUNDRY_CREDITORS'], LOCKED_GROUPS_ID['SUNDRY_DEBTORS']])
        return form

    def form_valid(self, form):
        context = self.get_context_data()
        expense_item_formset = context['expense_item_formset']
        if expense_item_formset.is_valid():
            with transaction.atomic():
                expense = form.save()
                expense_item_formset.instance = expense
                expense_item_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        print(form.errors)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ExpenseUpdateView(mixins.HybridUpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "transactions/expense_form.html"
    exclude = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_form'] = ItemForm(self.request.POST or None)
        context['expense_category_form'] = AccountForm(locked_group_id=LOCKED_GROUPS_ID['INDIRECT_EXPENSE'])
        context['account_form'] = AccountForm(locked_group_id=LOCKED_GROUPS_ID['SUNDRY_CREDITORS'])
        context['expense_item_formset'] = ExpenseItemFormSet(self.request.POST or None, instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        expense_item_formset = context['expense_item_formset']
        if expense_item_formset.is_valid():
            with transaction.atomic():
                expense = form.save()
                expense_item_formset.instance = expense
                expense_item_formset.save()
        return super().form_valid(form)


class ExpenseDeleteView(mixins.HybridDeleteView):
    model = Expense


class ItemListView(mixins.HybridListView):
    model = Item
    table_class = tables.ItemTable


class ItemDetailView(mixins.HybridDetailView):
    model = Item


class ItemCreateView(mixins.HybridCreateView):
    model = Item


class ItemUpdateView(mixins.HybridUpdateView):
    model = Item


class ItemDeleteView(mixins.HybridDeleteView):
    model = Item


class TransactionBaseListView(mixins.HybridListView):
    model = Transaction
    filterset_fields = {"voucher_no": ['icontains'], "date": ['exact'], "main_account": ['exact'], "opposite_account": ['exact']}
    search_fields = ("voucher_no", "main_account__name", "opposite_account__name")
    title = ""
    new_link = ""
    transaction_type = ""
    payment_method = ""

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(transaction_type=self.transaction_type, payment_method=self.payment_method)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['new_link'] = self.new_link
        return context


class TransactionBaseCreateView(mixins.HybridCreateView):
    template_name = "transactions/transaction_form.html"
    model = Transaction
    exclude = None
    form_set = ""
    transaction_type = ""
    payment_method = ""
    success_url = ""

    def generate_voucher_no(self):
        try:
            # Fetch settings for the current branch
            branch_settings = Setting.objects.filter(branch_id=self.request.session.get('branch')).first()
            if branch_settings and self.transaction_type == 'RECEIPT':
                receipt_settings = branch_settings.document_settings['receipt']  # Assuming it's stored as JSON or dictionary
                prefix = receipt_settings.get('prefix', 'RCPT')  # Default to 'RCPT' if prefix not found
                start_count = receipt_settings.get('start_count', 1000)  # Default start count if missing
            elif branch_settings and self.transaction_type == 'PAYMENT':
                payment_settings = branch_settings.document_settings['payment']
                prefix = payment_settings.get('prefix', 'PY')
                start_count = payment_settings.get('start_count', 1000)
            elif branch_settings and self.transaction_type == 'JV':
                payment_settings = branch_settings.document_settings['jv']
                prefix = payment_settings.get('prefix', 'JV')
                start_count = payment_settings.get('start_count', 1000)
            else:
                prefix = 'PY' if self.transaction_type == 'PAYMENT' else 'RCPT'
                start_count = 1000  # Default starting value
        except Exception as e:
            # Log the error instead of failing silently
            print(f"Error fetching settings: {e}")
            prefix = 'PY' if self.transaction_type == 'PAYMENT' else 'RCPT'
            start_count = 1000  # Default starting value

        # Get the last transaction number for the given type
        last_transaction = Transaction.objects.filter(is_active=True, voucher_no__startswith=prefix, transaction_type=self.transaction_type).aggregate(Max("voucher_no"))[
            "voucher_no__max"
        ]

        # Determine the next voucher number
        if last_transaction:
            try:
                next_number = int(last_transaction.replace(prefix, "")) + 1
            except ValueError:
                next_number = start_count
        else:
            next_number = start_count

        return f"{prefix}{next_number:04d}"

    def get_success_url(self):
        return self.success_url

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        if self.payment_method == 'BANK':
            form.fields['main_account'].queryset = form.fields['main_account'].queryset.filter(under_id=LOCKED_GROUPS_ID['BANK_ACCOUNT'])
        form.fields['opposite_account'].queryset = form.fields['opposite_account'].queryset.filter(
            under__id__in=[LOCKED_GROUPS_ID['SUNDRY_CREDITORS'], LOCKED_GROUPS_ID['SUNDRY_DEBTORS']]
        )
        form.fields['voucher_no'].initial = self.generate_voucher_no()
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.transaction_type == 'JV':
            kwargs['transaction_type'] = self.transaction_type
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"New {self.payment_method} {self.transaction_type}"
        context['sub_title'] = f"{self.payment_method} {self.transaction_type} Form"
        if self.form_set:
            context['form_set'] = self.form_set(self.request.POST or None)
        context['customer_form'] = AccountForm(locked_group_id=LOCKED_GROUPS_ID['SUNDRY_DEBTORS'])
        context['bank_form'] = AccountForm(locked_group_id=LOCKED_GROUPS_ID['BANK_ACCOUNT'])
        context['transaction_type'] = self.transaction_type
        context['payment_method'] = self.payment_method
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context.get('form_set') if self.form_set else None

        instance = form.instance
        instance.transaction_type = self.transaction_type
        instance.payment_method = self.payment_method

        if self.payment_method == 'CASH':
            instance.main_account_id = LOCKED_ACCOUNTS_ID['cash_account']

        try:
            with transaction.atomic():
                transaction_instance = form.save()

                # Only process formset if it exists and contains data
                if formset and formset.is_valid():
                    formset.instance = transaction_instance
                    formset.save()
                elif formset and not formset.is_valid():
                    form.add_error(None, "There was an error in the formset. Please review the entered data.")
                    return self.form_invalid(form)
        except Exception as e:
            print(f"Error: {e}")
            form.add_error(None, "An unexpected error occurred. Please try again.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form validation failed. Errors:", form.errors)
        return super().form_invalid(form)


class TransactionBaseUpdateView(mixins.HybridUpdateView):
    model = Transaction
    exclude = None
    form_set = ""
    transaction_type = ""
    payment_method = ""
    success_url = ""
    template_name = "transactions/transaction_form.html"

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit {self.payment_method} {self.transaction_type}"
        context['sub_title'] = f"{self.payment_method} {self.transaction_type} Form"
        context['customer_form'] = AccountForm(locked_group_id=LOCKED_GROUPS_ID['SUNDRY_DEBTORS'])
        context['bank_form'] = AccountForm(locked_group_id=LOCKED_GROUPS_ID['BANK_ACCOUNT'])

        # Handle optional formset
        if self.form_set:
            context['form_set'] = self.form_set(self.request.POST or None, instance=self.object)
        else:
            context['form_set'] = None

        context['transaction_type'] = self.transaction_type
        context['payment_method'] = self.payment_method
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context.get('form_set')

        try:
            with transaction.atomic():
                transaction_instance = form.save()

                # Only validate and save formset if it exists
                if formset:
                    if formset.is_valid():
                        formset.instance = transaction_instance
                        formset.save()
                    else:
                        form.add_error(None, "There was an error in the formset. Please review the entered data.")
                        return self.form_invalid(form)
        except Exception as e:
            print(f"Error: {e}")
            form.add_error(None, "An unexpected error occurred. Please try again.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form validation failed. Errors:", form.errors)
        return super().form_invalid(form)


class CashReceiptListView(TransactionBaseListView):
    title = "Cash Receipts"
    new_link = reverse_lazy('transactions:cash_receipt_create')
    transaction_type = "RECEIPT"
    payment_method = "CASH"
    table_class = tables.CashReceiptTransactionTable


class BankReceiptListView(TransactionBaseListView):
    title = "Bank Receipts"
    new_link = reverse_lazy('transactions:bank_receipt_create')
    transaction_type = "RECEIPT"
    payment_method = "BANK"
    table_class = tables.BankReceiptTransactionTable


class CashPaymentListView(TransactionBaseListView):
    title = "Cash Payments"
    new_link = reverse_lazy('transactions:cash_payment_create')
    transaction_type = "PAYMENT"
    payment_method = "CASH"
    table_class = tables.CashPaymentTransactionTable


class BankPaymentListView(TransactionBaseListView):
    title = "Bank Payments"
    new_link = reverse_lazy('transactions:bank_payment_create')
    transaction_type = "PAYMENT"
    payment_method = "BANK"
    table_class = tables.BankPaymentTransactionTable


class BankReceiptCreateView(TransactionBaseCreateView):
    form_class = forms.BankTransactionForm
    form_set = forms.ReceiptTransactionItemFormSet
    transaction_type = "RECEIPT"
    payment_method = "BANK"
    success_url = reverse_lazy("transactions:bank_receipt_list")


class CashReceiptCreateView(TransactionBaseCreateView):
    form_class = forms.CashTransactionForm
    form_set = forms.ReceiptTransactionItemFormSet
    transaction_type = "RECEIPT"
    payment_method = "CASH"
    success_url = reverse_lazy("transactions:cash_receipt_list")


class BankPaymentCreateView(TransactionBaseCreateView):
    form_class = forms.BankTransactionForm
    form_set = forms.PaymentTransactionItemFormSet
    transaction_type = "PAYMENT"
    payment_method = "BANK"
    success_url = reverse_lazy("transactions:bank_payment_list")


class CashPaymentCreateView(TransactionBaseCreateView):
    form_class = forms.CashTransactionForm
    form_set = forms.PaymentTransactionItemFormSet
    transaction_type = "PAYMENT"
    payment_method = "CASH"
    success_url = reverse_lazy("transactions:cash_payment_list")


class BankReceiptUpdateView(TransactionBaseUpdateView):
    form_class = forms.BankTransactionForm
    form_set = forms.ReceiptTransactionItemFormSet
    transaction_type = "RECEIPT"
    payment_method = "BANK"
    success_url = reverse_lazy("transactions:bank_receipt_list")


class CashReceiptUpdateView(TransactionBaseUpdateView):
    form_class = forms.CashTransactionForm
    form_set = forms.ReceiptTransactionItemFormSet
    transaction_type = "RECEIPT"
    payment_method = "CASH"
    success_url = reverse_lazy("transactions:cash_receipt_list")


class BankPaymentUpdateView(TransactionBaseUpdateView):
    form_class = forms.BankTransactionForm
    form_set = forms.PaymentTransactionItemFormSet
    transaction_type = "PAYMENT"
    payment_method = "BANK"
    success_url = reverse_lazy("transactions:bank_payment_list")


class CashPaymentUpdateView(TransactionBaseUpdateView):
    form_class = forms.CashTransactionForm
    form_set = forms.PaymentTransactionItemFormSet
    transaction_type = "PAYMENT"
    payment_method = "CASH"
    success_url = reverse_lazy("transactions:cash_payment_list")


class TransactionDetailView(mixins.HybridDetailView):
    model = Transaction


class TrsansactionDeleteView(mixins.HybridDeleteView):
    model = Transaction


class JournalVoucherListView(TransactionBaseListView):
    title = "Journal Voucher"
    new_link = reverse_lazy('transactions:journal_voucher_create')
    transaction_type = 'JV'
    payment_method = None
    table_class = tables.JournalVoucherTable


class JournalVoucherCreateView(TransactionBaseCreateView):
    form_class = forms.JournalVoucherForm
    form_set = None
    transaction_type = "JV"
    payment_method = None
    success_url = reverse_lazy("transactions:journal_voucher_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'New Journal Voucher'
        context['sub_title'] = 'Journal Voucher Form'
        return context


class JournalVoucherUpdateView(TransactionBaseUpdateView):
    form_class = forms.JournalVoucherForm
    form_set = None
    transaction_type = "JV"
    payment_method = None
    success_url = reverse_lazy("transactions:journal_voucher_list")
