from core.base import BaseForm
from django.db import transaction
from django.db.models import Sum
from .models import Admission, Attendance, FeeReceipt, FeeStructure, StudentFee, AdmissionEnquiry, AttendanceRegister
from django import forms
from decimal import Decimal
from branches.models import Branch
from employees.models import Employee


class AdmissionForm(BaseForm):
    class Meta:
        model = Admission
        exclude = ("user", "branch",)


class AdmissionPhotoForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['photo']
        widgets = {'photo': forms.FileInput(attrs={'class': 'form-control d-none'})}


class AdmissionPersonalDataForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = (
            "is_active",
            "first_name",
            "last_name",
            "personal_email",
            "gender",
            "contact_number",
            "whatsapp_number",
            "date_of_birth",
            "religion",
            "blood_group",
            "qualifications",
            "photo",
        )

    def __init__(self, *args, **kwargs):
        super(AdmissionPersonalDataForm, self).__init__(*args, **kwargs)
        self.fields['qualifications'].widget.attrs['rows'] = 3


class AdmissionParentDataForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ("is_active", "parent_first_name", "parent_last_name", "parent_contact_number", "parent_whatsapp_number", "parent_mail_id",)


class AdmissionAddressDataForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ("is_active", "home_address", "city", "district", "state", "pin_code",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['home_address'].widget.attrs['rows'] = 3


class AdmissionOfficialDataForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = (
            "is_active",
            "joining_date",
            "admission_date",
            "course",
            "batch",
            "other_details",
            "document",
            "signature",
        )


class AdmissionFinancialDataForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ("fee_type", "is_discount", "discount_amount")
        widgets = {
            'fee_type': forms.Select(attrs={'class': 'select form-control', 'id': 'id_fee_type'}),
            'is_discount': forms.Select(attrs={'class': 'select form-control', 'id': 'id_is_discount'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'id': 'discount_amount'}),
        }

    def save(self, commit=True):
        admission = super().save(commit=False)

        with transaction.atomic():
            fee_names = ["first_payment", "second_payment", "third_payment", "fourth_payment"]

            if not StudentFee.objects.filter(student=admission).exists():
                for fee_name in fee_names:
                    fee_structure = FeeStructure.objects.filter(course=admission.course, name=fee_name).first()
                    if fee_structure:
                        StudentFee.objects.create(student=admission, fee_structure=fee_structure)

            if commit:
                admission.save() 


        return admission

        

class AttendanceForm(BaseForm):
    student_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    student_pk = forms.IntegerField(widget=forms.HiddenInput())  

    class Meta:
        model = Attendance
        fields = ('status',)  
        widgets = {
            'status': forms.Select(attrs={'class': 'select form-control', 'required': True}),
        }


class AttendanceUpdateForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ('status','student' )  
        widgets = {
            'status': forms.Select(attrs={'class': 'select form-control', 'required': True}),
            'student': forms.Select(attrs={'class': 'select form-control', 'required': True}),
        }


class StudentFeeOverviewForm(forms.ModelForm):
    
    class Meta:
        model = Admission
        fields = ("first_name", "admission_number", "course", )
        
    
class FeeReceiptForm(forms.ModelForm):
    class Meta:
        model = FeeReceipt
        fields = ("student", "receipt_no", "date", "payment_type", "amount")

# Define the inline formset
FeeReceiptFormSet = forms.inlineformset_factory(
    Admission, 
    FeeReceipt,  
    form=FeeReceiptForm,
    can_delete=True  
)

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}),
        label="Password"
    )
    
    class Meta:
        model = Admission
        fields = (
            "first_name", "last_name", "home_address", "contact_number", 
            "whatsapp_number", "joining_date", "date_of_birth", "city", "district", "state", "pin_code", "gender", "religion", "blood_group", 
            "personal_email", "parent_first_name", "parent_last_name", "parent_contact_number", 
            "parent_whatsapp_number", "parent_mail_id", "photo", "branch", "course", "batch", "qualifications", "document", "signature",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter First Name", }),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Last Name"}),
            "home_address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter Home Address"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Contact Number"}),
            "whatsapp_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter WhatsApp Number"}),
            "joining_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter City"}),
            "district": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter District"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter state"}),
            "pin_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Pin Code"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "religion": forms.Select(attrs={"class": "form-control"}),
            "blood_group": forms.Select(attrs={"class": "form-control"}),
            "personal_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter Email"}),
            "parent_first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Parent's First Name"}),
            "parent_last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Parent's Last Name"}),
            "parent_contact_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Parent's Contact Number"}),
            "parent_whatsapp_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Parent's WhatsApp Number"}),
            "parent_mail_id": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter Parent's Email"}),
            "photo": forms.FileInput(attrs={"class": "form-control-file"}),
            "branch" : forms.Select(attrs={"class": "form-control"}),
            "course": forms.Select(attrs={"class": "form-control"}),
            "batch": forms.Select(attrs={"class": "form-control"}),
            "qualifications": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Education Qualification"}),
            "document" : forms.FileInput(attrs={"class": "form-control form-control-file"}),
            "signature" : forms.FileInput(attrs={"class": "form-control form-control-file"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['joining_date'].input_formats = ['%Y-%m-%d']
        self.fields['date_of_birth'].input_formats = ['%Y-%m-%d']

        required_fields = [
        "first_name", "last_name", "home_address", "contact_number",
        "whatsapp_number", "joining_date", "date_of_birth", "city", "district",
        "state", "pin_code", "gender", "religion", "blood_group", "personal_email",
        "parent_first_name", "parent_last_name", "parent_contact_number",
        "parent_whatsapp_number", "parent_mail_id", "photo", "branch", "course",
        "batch", "qualifications", "document", "signature", "password"
        ]
        for field in required_fields:
            self.fields[field].required = True

        

class AdmissionEnquiryForm(forms.ModelForm):
    class Meta:
        model = AdmissionEnquiry
        fields = '__all__'
        

class AttendanceRegisterForm(forms.ModelForm):
    starting_time = forms.TimeField(required=False, disabled=True)
    ending_time = forms.TimeField(required=False, disabled=True)

    class Meta:
        model = AttendanceRegister
        exclude = ('branch', 'batch')
        fields = ('date', 'course', 'starting_time', 'ending_time')

    def __init__(self, *args, batch=None, **kwargs):
        super().__init__(*args, **kwargs)
        if batch:
            self.fields['starting_time'].initial = batch.starting_time
            self.fields['ending_time'].initial = batch.ending_time

        
class FeeReceiptForm(forms.ModelForm):
    class Meta:
        model = FeeReceipt
        fields = '__all__'