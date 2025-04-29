from .models import Account
from .models import GroupMaster
from django import forms


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ("creator",)

    def __init__(self, *args, **kwargs):
        locked_group_id = kwargs.pop("locked_group_id", None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        if locked_group_id:
            if isinstance(locked_group_id, list) and locked_group_id:  # Check if it's a non-empty list
                self.fields['under'].queryset = self.fields['under'].queryset.filter(id__in=locked_group_id)
            elif not isinstance(locked_group_id, list):  # If it's not a list, use it directly
                self.fields['under'].initial = locked_group_id
                self.fields['under'].queryset = self.fields['under'].queryset.filter(id=locked_group_id)


class GroupMasterForm(forms.ModelForm):
    class Meta:
        model = GroupMaster
        fields = ("code", "name", "nature_of_group", "main_group", "description")


# class BankTransactionForm(forms.ModelForm):
#     main_account = forms.ModelChoiceField(
#         queryset=Account.objects.filter(under_id=LOCKED_GROUPS_ID['BANK_ACCOUNT']),
#         label="Bank Account"
#     )
#     class Meta:
#         model = Transaction
#         exclude = ("document_no","document_date","transaction_type")


# class CashTransactionForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         exclude = ("cheque_no","cheque_date","transaction_type","cheque_name")

#     main_account = forms.ModelChoiceField(
#         queryset=Account.objects.filter(under_id=LOCKED_GROUPS_ID['CASH_ACCOUNT']),
#         label="Cash Account"
#     )

# class ExpenseForm(forms.ModelForm):
#     auto_round_off = forms.BooleanField(
#         required=False,
#         label="Round Off",
#         widget=forms.CheckboxInput(attrs={'id': 'id_auto_round_off'}),
#         initial=False,
#     )

#     class Meta:
#         model = Expense
#         exclude = ("creator", "status")
#         widgets = {
#             "expense_no": forms.TextInput(attrs={"class": "form-control py-0"}),
#             "bill_date": forms.DateInput(attrs={"class": "form-control py-0 dateinput"}),
#             "total_tax_amount": forms.NumberInput(attrs={"class": "custom-input", "readonly": "readonly"}),
#             "items_discount_total": forms.NumberInput(attrs={"class": "custom-input", "readonly": "readonly"}),
#             "sub_total": forms.NumberInput(attrs={"class": "custom-input", "readonly": "readonly"}),
#             "total_quantity": forms.NumberInput(attrs={"class": "custom-input", "readonly": "readonly"}),
#             "discount_percentage": forms.NumberInput(attrs={"placeholder": "%"}),
#             "discount_amount": forms.NumberInput(attrs={"placeholder": "₹"}),
#             "round_off": forms.NumberInput(attrs={"class":"w-50","readonly": "readonly"}),
#             "grand_total": forms.NumberInput(attrs={"readonly": "readonly"}),
#             "taxable_amount": forms.NumberInput(attrs={"readonly": "readonly"}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Apply common class to all fields except auto_round_off
#         common_class = "form-control"
#         for field_name, field in self.fields.items():
#             if field_name != "auto_round_off":
#                 field.widget.attrs.update({"class": f"{common_class} {field.widget.attrs.get('class', '')}".strip()})


# class ExpenseItemForm(forms.ModelForm):
#     class Meta:
#         model = ExpenseItem
#         fields = ("item","quantity","unit_price","discount_percentage","discount_amount","tax","tax_amount","line_total")
#         widgets = {
#             "item": forms.Select(attrs={"class": "form-control item-select"}),
#             "quantity": forms.NumberInput(attrs={"class": "form-control quantity-input", "min": 1, "step": 1}),
#             "unit_price": forms.NumberInput(attrs={"class": "form-control unit-price-input"}),
#             "discount_percentage": forms.NumberInput(attrs={"class": "form-control discount_percentage-input", "placeholder": " %"}),
#             "discount_amount": forms.NumberInput(attrs={"class": "form-control discount_amount-input", "placeholder": "₹"}),
#             "tax": forms.Select(attrs={"class": "form-control tax-input"}),
#             "tax_amount": forms.NumberInput(attrs={"class": "form-control tax_amount-input", "readonly": "readonly"}),
#             "line_total": forms.NumberInput(attrs={"class": "form-control line_total-input", "readonly": "readonly"}),
#         }


# ExpenseItemFormSet = forms.inlineformset_factory(
#     Expense,
#     ExpenseItem,
#     form=ExpenseItemForm,
#     extra=1,
#     can_delete=True
# )

# class ItemForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = ("is_active","name","hsn_or_sac","price","tax_included","tax")

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'
