from core.base import BaseForm
from invoices.models import Invoice

from .models import Expense
from .models import ExpenseItem
from .models import Item
from .models import Transaction
from .models import TransactionItem
from django import forms
from django.contrib.contenttypes.models import ContentType


class ExpenseForm(BaseForm):
    auto_round_off = forms.BooleanField(
        required=False, label="Round Off", widget=forms.CheckboxInput(attrs={'id': 'id_auto_round_off', "role": "switch", "class": "form-check-input"}), initial=False
    )

    class Meta:
        model = Expense
        exclude = ("creator", "status")
        widgets = {
            "expense_no": forms.TextInput(attrs={"class": "form-control "}),
            "bill_date": forms.DateInput(attrs={"class": "form-control  dateinput"}),
            "total_tax_amount": forms.NumberInput(attrs={"class": "custom-input", "readonly": "readonly"}),
            "items_discount_total": forms.NumberInput(attrs={"class": "custom-input", "readonly": "readonly"}),
            "sub_total": forms.NumberInput(attrs={"class": "custom-input", "readonly": "readonly"}),
            "total_quantity": forms.NumberInput(attrs={"class": "custom-input", "readonly": "readonly"}),
            "discount_percentage": forms.NumberInput(attrs={"placeholder": "%"}),
            "discount_amount": forms.NumberInput(attrs={"placeholder": "₹"}),
            "round_off": forms.NumberInput(attrs={"class": "w-50", "readonly": "readonly"}),
            "grand_total": forms.NumberInput(attrs={"readonly": "readonly"}),
            "taxable_amount": forms.NumberInput(attrs={"readonly": "readonly"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply common class to all fields except auto_round_off
        common_class = "form-control"
        for field_name, field in self.fields.items():
            if field_name != "auto_round_off":
                field.widget.attrs.update({"class": f"{common_class} {field.widget.attrs.get('class', '')}".strip()})


class ExpenseItemForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ("item", "quantity", "unit_price", "discount_percentage", "discount_amount", "tax", "tax_amount", "line_total")
        widgets = {
            "item": forms.Select(attrs={"class": "form-control item-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control quantity-input", "min": 1, "step": 1}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control unit-price-input"}),
            "discount_percentage": forms.NumberInput(attrs={"class": "form-control discount_percentage-input", "placeholder": " %"}),
            "discount_amount": forms.NumberInput(attrs={"class": "form-control discount_amount-input", "placeholder": "₹"}),
            "tax": forms.NumberInput(attrs={"class": "form-control tax-input", "placeholder": "%"}),
            "tax_amount": forms.NumberInput(attrs={"class": "form-control tax_amount-input", "readonly": "readonly"}),
            "line_total": forms.NumberInput(attrs={"class": "form-control line_total-input", "readonly": "readonly"}),
        }


ExpenseItemFormSet = forms.inlineformset_factory(Expense, ExpenseItem, form=ExpenseItemForm, extra=1, can_delete=True)


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ("is_active", "name", "hsn_or_sac", "price", "tax_included", "tax")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BaseTransactionForm(BaseForm):
    class Meta:
        model = Transaction
        fields = ("date", "opposite_account", "voucher_no", "reference", "amount", "remark", "narration")


class BankTransactionForm(BaseTransactionForm):
    class Meta(BaseTransactionForm.Meta):
        fields = BaseTransactionForm.Meta.fields + ("main_account", "cheque_no", "cheque_date", "transfer_method", "cheque_name")

    def __init__(self, *args, **kwargs):
        transaction_type = kwargs.pop('transaction_type', None)
        super().__init__(*args, **kwargs)
        self.fields['main_account'].label = "Drawn Bank & Branch"
        if transaction_type == "RECEIPT":
            self.fields['opposite_account'].label = "Customer"
        elif transaction_type == "PAYMENT":
            self.fields['opposite_account'].label = "Supplier"


class CashTransactionForm(BaseTransactionForm):
    denomination_units = [2000, 500, 200, 100, 50, 20, 10, 5, 2, 1]

    for unit in denomination_units:
        locals()[f'denomination_{unit}_unit'] = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control py-0'}))
        locals()[f'denomination_{unit}_unit_total'] = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control py-0', 'readonly': 'readonly'}))

    is_denomination = forms.BooleanField(required=False, label="Denomination", widget=forms.CheckboxInput(attrs={"role": "switch", "class": "form-check-input"}), initial=False)

    class Meta(BaseTransactionForm.Meta):
        fields = BaseTransactionForm.Meta.fields + ("document_no", "document_date", "is_denomination")

    def __init__(self, *args, **kwargs):
        transaction_type = kwargs.pop('transaction_type', None)
        super().__init__(*args, **kwargs)

        # Set labels based on transaction type
        if transaction_type == "RECEIPT":
            self.fields['opposite_account'].label = "Customer"
        elif transaction_type == "PAYMENT":
            self.fields['opposite_account'].label = "Supplier"

        # Load existing denomination data if form is used for updating
        if self.instance and self.instance.pk and self.instance.denomination:
            for unit in self.denomination_units:
                field_name = f'denomination_{unit}_unit'
                f'denomination_{unit}_unit_total'
                if field_name in self.fields and str(unit) in self.instance.denomination:
                    self.fields[field_name].initial = self.instance.denomination.get(str(unit), 0)

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Collect denomination data
        denomination_data = {}
        for unit in self.denomination_units:
            field_name = f'denomination_{unit}_unit'
            value = self.cleaned_data.get(field_name, 0)
            if value:
                denomination_data[str(unit)] = float(value)  # Store as JSON serializable format

        instance.denomination = denomination_data

        if commit:
            instance.save()
        return instance


class ReceiptTransactionItemForm(BaseForm):
    reference = forms.ModelChoiceField(queryset=Invoice.objects.filter(is_active=True), required=False, widget=forms.Select(attrs={'class': 'form-control reference-input'}))
    date = forms.DateField(required=False, widget=forms.TextInput(attrs={"class": "form-control date-input"}))
    pending = forms.DecimalField(required=False, widget=forms.TextInput(attrs={"class": "form-control pending-input"}))
    tds = forms.DecimalField(required=False, widget=forms.TextInput(attrs={"class": "form-control tds-input"}))
    discount = forms.DecimalField(required=False, widget=forms.TextInput(attrs={"class": "form-control discount-input"}))

    class Meta:
        model = TransactionItem
        fields = ("amount",)
        widgets = {"amount": forms.NumberInput(attrs={'class': 'form-control received-input'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # Retrieve the related reference using GenericForeignKey
            reference_instance = None
            if self.instance.content_type and self.instance.object_id:
                reference_instance = self.instance.content_type.get_object_for_this_type(id=self.instance.object_id)

            # Populate fields with existing instance values
            self.fields["reference"].initial = reference_instance
            self.fields["date"].initial = getattr(reference_instance, "date", None)
            self.fields["pending"].initial = getattr(reference_instance, "pending", None)
            self.fields["tds"].initial = getattr(reference_instance, "tds", None)
            self.fields["discount"].initial = getattr(reference_instance, "discount", None)
            self.fields["amount"].initial = self.instance.amount

        for field_name, field in self.fields.items():
            field.required = False
            if field_name not in ["amount"]:
                field.widget.attrs["readonly"] = True
            if self.initial.get(field_name) is not None:
                field.initial = self.initial[field_name]

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference = self.cleaned_data.get("reference")
        amount = self.cleaned_data.get("amount")
        # Ensure amount is explicitly checked
        if amount is not None:
            if reference:
                # Set content_type and object_id for the GenericForeignKey
                instance.content_type = ContentType.objects.get_for_model(reference)
                instance.object_id = reference.id

            if commit:
                instance.save()
                print("saved", instance)
            return instance

        print("Skipped saving instance due to missing amount")
        return None  # Return None if amount is missing


ReceiptTransactionItemFormSet = forms.inlineformset_factory(Transaction, TransactionItem, form=ReceiptTransactionItemForm, can_delete=True, extra=1)


class PaymentTransactionItemForm(BaseForm):
    reference = forms.ModelChoiceField(queryset=Invoice.objects.filter(is_active=True))

    class Meta:
        model = TransactionItem
        fields = ("amount",)

    def save(self, commit=True):
        instance = super().save(commit=False)
        reference = self.cleaned_data.get('reference')

        # Set content_type and object_id for the GenericForeignKey
        instance.content_type = ContentType.objects.get_for_model(reference)
        instance.object_id = reference.id

        if commit:
            instance.save()
        return instance


PaymentTransactionItemFormSet = forms.inlineformset_factory(Transaction, TransactionItem, form=PaymentTransactionItemForm, can_delete=True, extra=1)


class JournalVoucherForm(BaseTransactionForm):
    class Meta(BaseTransactionForm.Meta):
        fields = BaseTransactionForm.Meta.fields + ("main_account",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['main_account'].label = "Debit Account"
        self.fields['opposite_account'].label = "Credit Account"
