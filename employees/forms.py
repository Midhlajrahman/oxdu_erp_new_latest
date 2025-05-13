from core.base import BaseForm

from .models import Department
from .models import Designation
from .models import Employee
from masters.models import Course
from django import forms


class DepartmentForm(BaseForm):
    class Meta:
        model = Department
        fields = "__all__"


class DesignationForm(BaseForm):
    class Meta:
        model = Designation
        fields = "__all__"
        
    
class CourseForm(BaseForm):
    class Meta:
        model = Course
        fields = "__all__"


class EmployeeForm(BaseForm):
    class Meta:
        model = Employee
        exclude = ("user", "status", "resigned_date", "notice_date", "resigned_form", "termination_date", "termination_reason")


class EmployeePhotoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['photo']
        widgets = {'photo': forms.FileInput(attrs={'class': 'form-control d-none'})}


class EmployeePersonalDataForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            "is_active",
            "first_name",
            "last_name",
            "personal_email",
            "gender",
            "marital_status",
            "mobile",
            "whatsapp",
            "date_of_birth",
            "religion",
            "blood_group",
            "experience",
            "qualifications",
            "photo",
        )

    def __init__(self, *args, **kwargs):
        super(EmployeePersonalDataForm, self).__init__(*args, **kwargs)
        self.fields['experience'].widget.attrs['rows'] = 3
        self.fields['qualifications'].widget.attrs['rows'] = 3


class EmployeeParentDataForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ("is_active", "father_name", "father_mobile", "mother_name", "guardian_name", "guardian_mobile", "relationship_with_employee")


class EmployeeAddressDataForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ("is_active", "type_of_residence", "residence_name", "residential_address", "residence_contact", "residential_zip_code", "permanent_address", "permanent_zip_code")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['residential_address'].widget.attrs['rows'] = 3
        self.fields['permanent_address'].widget.attrs['rows'] = 3


class EmployeeOfficialDataForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            "is_active",
            "employee_id",
            "department",
            "designation",
            "course",
            "is_also_tele_caller",
            "date_of_confirmation",
            "date_of_joining",
            "official_email",
            "employment_type",
            "offer_letter",
            "joining_letter",
            "agreement_letter",
            "experience_letter",
        )


class EmployeeFinancialDataForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ("is_active", "bank_name", "account_name", "bank_branch", "account_number", "ifsc_code", "basic_salary", "hra", "transportation_allowance", "other_allowance")
