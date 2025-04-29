from .models import AcademicYear
from branches.models import Branch
from .models import LockingAccount
from .models import LockingGroup
from .models import Setting
from django import forms


class SettingForm(forms.ModelForm):
    # Invoice fields
    airline_invoice_prefix = forms.CharField(max_length=4, initial="AI", label="Airline Invoice Prefix")
    airline_invoice_start_count = forms.IntegerField(initial=1000, label="Airline Invoice Start Count")
    hotel_invoice_prefix = forms.CharField(max_length=4, initial="HT", label="Hotel Invoice Prefix")
    hotel_invoice_start_count = forms.IntegerField(initial=2000, label="Hotel Invoice Start Count")
    visa_invoice_prefix = forms.CharField(max_length=4, initial="VI", label="Visa Invoice Prefix")
    visa_invoice_start_count = forms.IntegerField(initial=3000, label="Visa Invoice Start Count")
    miscellaneous_invoice_prefix = forms.CharField(max_length=4, initial="MS", label="Miscellaneous Invoice Prefix")
    miscellaneous_invoice_start_count = forms.IntegerField(initial=4000, label="Miscellaneous Invoice Start Count")
    transportation_invoice_prefix = forms.CharField(max_length=4, initial="TR", label="Transportation Invoice Prefix")
    transportation_invoice_start_count = forms.IntegerField(initial=5000, label="Transportation Invoice Start Count")
    package_invoice_prefix = forms.CharField(max_length=4, initial="TR", label="Package Invoice Prefix")
    package_invoice_start_count = forms.IntegerField(initial=5000, label="Package Invoice Start Count")

    # Purchase fields
    airline_purchase_prefix = forms.CharField(max_length=4, initial="PA", label="Airline Purchase Prefix")
    airline_purchase_start_count = forms.IntegerField(initial=1000, label="Airline Purchase Start Count")
    hotel_purchase_prefix = forms.CharField(max_length=4, initial="PH", label="Hotel Purchase Prefix")
    hotel_purchase_start_count = forms.IntegerField(initial=2000, label="Hotel Purchase Start Count")
    visa_purchase_prefix = forms.CharField(max_length=4, initial="PV", label="Visa Purchase Prefix")
    visa_purchase_start_count = forms.IntegerField(initial=3000, label="Visa Purchase Start Count")
    miscellaneous_purchase_prefix = forms.CharField(max_length=4, initial="PM", label="Miscellaneous Purchase Prefix")
    miscellaneous_purchase_start_count = forms.IntegerField(initial=4000, label="Miscellaneous Purchase Start Count")
    transportation_purchase_prefix = forms.CharField(max_length=4, initial="PT", label="Transportation Purchase Prefix")
    transportation_purchase_start_count = forms.IntegerField(initial=5000, label="Transportation Purchase Start Count")
    package_purchase_prefix = forms.CharField(max_length=4, initial="PT", label="Package Purchase Prefix")
    package_purchase_start_count = forms.IntegerField(initial=5000, label="Package Purchase Start Count")
    # estimate
    airline_estimate_prefix = forms.CharField(max_length=4, initial="QTAI", label="Airline Estimate Prefix")
    airline_estimate_start_count = forms.IntegerField(initial=1, label="Airline Estimate Start Count")
    hotel_estimate_prefix = forms.CharField(max_length=4, initial="QTHT", label="Hotel Estimate Prefix")
    hotel_estimate_start_count = forms.IntegerField(initial=1, label="Hotel Estimate Start Count")
    visa_estimate_prefix = forms.CharField(max_length=4, initial="QTVI", label="Visa Estimate Prefix")
    visa_estimate_start_count = forms.IntegerField(initial=1, label="Visa Estimate Start Count")
    miscellaneous_estimate_prefix = forms.CharField(max_length=4, initial="QTMS", label="Miscellaneous Estimate Prefix")
    miscellaneous_estimate_start_count = forms.IntegerField(initial=1, label="Miscellaneous Estimate Start Count")
    transportation_estimate_prefix = forms.CharField(max_length=4, initial="QTTR", label="Transportation Estimate Prefix")
    transportation_estimate_start_count = forms.IntegerField(initial=1, label="Transportation Estimate Start Count")
    package_estimate_prefix = forms.CharField(max_length=4, initial="QTPA", label="Package Estimate Prefix")
    package_estimate_start_count = forms.IntegerField(initial=1, label="Package Estimate Start Count")
    #
    receipt_prefix = forms.CharField(max_length=4, initial="RCPT", label="Receipt Prefix")
    receipt_start_count = forms.IntegerField(initial=1, label="Receipt Start Count")
    payment_prefix = forms.CharField(max_length=4, initial="PY", label="Payment Prefix")
    payment_start_count = forms.IntegerField(initial=1, label="Payment Start Count")
    journal_voucher_prefix = forms.CharField(max_length=4, initial="JV", label="Journal Voucher Prefix")
    journal_voucher_start_count = forms.IntegerField(initial=1, label="Journal Voucher Start Count")

    class Meta:
        model = Setting
        fields = ['airline_invoice_prefix']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.document_settings:
            document_settings = self.instance.document_settings
            for doc_type, settings in document_settings.get("invoice", {}).items():
                self.fields[f"{doc_type}_invoice_prefix"].initial = settings.get("prefix", "")
                self.fields[f"{doc_type}_invoice_start_count"].initial = settings.get("start_count", 0)

            for doc_type, settings in document_settings.get("purchase", {}).items():
                self.fields[f"{doc_type}_purchase_prefix"].initial = settings.get("prefix", "")
                self.fields[f"{doc_type}_purchase_start_count"].initial = settings.get("start_count", 0)

            for doc_type, settings in document_settings.get("estimate", {}).items():
                self.fields[f"{doc_type}_estimate_prefix"].initial = settings.get("prefix", "")
                self.fields[f"{doc_type}_estimate_start_count"].initial = settings.get("start_count", 0)

            payment_setting = document_settings.get("payment", {})
            self.fields['payment_prefix'].initial = payment_setting.get("prefix", "")
            self.fields['payment_start_count'].initial = payment_setting.get("start_count", 0)
            receipt_setting = document_settings.get("receipt", {})
            self.fields['receipt_prefix'].initial = receipt_setting.get("prefix", "")
            self.fields['receipt_start_count'].initial = receipt_setting.get("start_count", 0)
            journal_voucher_setting = document_settings.get("jv", {})
            self.fields['journal_voucher_prefix'].initial = journal_voucher_setting.get("prefix", "")
            self.fields['journal_voucher_start_count'].initial = journal_voucher_setting.get("start_count", 0)

    def save(self, commit=True):
        instance = super().save(commit=False)
        document_settings = {
            "invoice": {
                "airline": {"prefix": self.cleaned_data["airline_invoice_prefix"], "start_count": self.cleaned_data["airline_invoice_start_count"]},
                "hotel": {"prefix": self.cleaned_data["hotel_invoice_prefix"], "start_count": self.cleaned_data["hotel_invoice_start_count"]},
                "visa": {"prefix": self.cleaned_data["visa_invoice_prefix"], "start_count": self.cleaned_data["visa_invoice_start_count"]},
                "miscellaneous": {"prefix": self.cleaned_data["miscellaneous_invoice_prefix"], "start_count": self.cleaned_data["miscellaneous_invoice_start_count"]},
                "transportation": {"prefix": self.cleaned_data["transportation_invoice_prefix"], "start_count": self.cleaned_data["transportation_invoice_start_count"]},
                "package": {"prefix": self.cleaned_data["package_invoice_prefix"], "start_count": self.cleaned_data["package_invoice_start_count"]},
            },
            "purchase": {
                "airline": {"prefix": self.cleaned_data["airline_purchase_prefix"], "start_count": self.cleaned_data["airline_purchase_start_count"]},
                "hotel": {"prefix": self.cleaned_data["hotel_purchase_prefix"], "start_count": self.cleaned_data["hotel_purchase_start_count"]},
                "visa": {"prefix": self.cleaned_data["visa_purchase_prefix"], "start_count": self.cleaned_data["visa_purchase_start_count"]},
                "miscellaneous": {"prefix": self.cleaned_data["miscellaneous_purchase_prefix"], "start_count": self.cleaned_data["miscellaneous_purchase_start_count"]},
                "transportation": {"prefix": self.cleaned_data["transportation_purchase_prefix"], "start_count": self.cleaned_data["transportation_purchase_start_count"]},
                "package": {"prefix": self.cleaned_data["package_purchase_prefix"], "start_count": self.cleaned_data["package_purchase_start_count"]},
            },
            "estimate": {
                "airline": {"prefix": self.cleaned_data["airline_estimate_prefix"], "start_count": self.cleaned_data["airline_estimate_start_count"]},
                "hotel": {"prefix": self.cleaned_data["hotel_estimate_prefix"], "start_count": self.cleaned_data["hotel_estimate_start_count"]},
                "visa": {"prefix": self.cleaned_data["visa_estimate_prefix"], "start_count": self.cleaned_data["visa_estimate_start_count"]},
                "miscellaneous": {"prefix": self.cleaned_data["miscellaneous_estimate_prefix"], "start_count": self.cleaned_data["miscellaneous_estimate_start_count"]},
                "transportation": {"prefix": self.cleaned_data["transportation_estimate_prefix"], "start_count": self.cleaned_data["transportation_estimate_start_count"]},
                "package": {"prefix": self.cleaned_data["package_estimate_prefix"], "start_count": self.cleaned_data["package_estimate_start_count"]},
            },
            "receipt": {"prefix": self.cleaned_data['receipt_prefix'], "start_count": self.cleaned_data['receipt_start_count']},
            "payment": {"prefix": self.cleaned_data['payment_prefix'], "start_count": self.cleaned_data['payment_start_count']},
            "jv": {"prefix": self.cleaned_data['journal_voucher_prefix'], "start_count": self.cleaned_data['journal_voucher_start_count']},
        }
        instance.document_settings = document_settings
        if commit:
            instance.save()
        return instance


class LockingGroupForm(forms.ModelForm):
    class Meta:
        model = LockingGroup
        fields = ("name", "group")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-select'


LockingGroupFormSet = forms.modelformset_factory(LockingGroup, form=LockingGroupForm, extra=1)


class LockingAccountForm(forms.ModelForm):
    class Meta:
        model = LockingAccount
        fields = ("name", "account")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-select'


LockingAccountFormSet = forms.modelformset_factory(LockingAccount, form=LockingAccountForm, extra=1)


class HomeForm(forms.Form):
    branch = forms.ModelChoiceField(queryset=Branch.objects.filter(is_active=True))
    academic_year = forms.ModelChoiceField(queryset=AcademicYear.objects.all())
