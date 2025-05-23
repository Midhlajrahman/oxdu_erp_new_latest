import os
import uuid

from core.base import BaseModel
from core.choices import BLOOD_CHOICES, RELIGION_CHOICES
from core.choices import EMPLOYEE_STATUS_CHOICES
from core.choices import EMPLOYMENT_TYPE_CHOICES
from core.choices import GENDER_CHOICES
from core.choices import MARITAL_CHOICES
from core.choices import RESIDENCE_CHOICES

from django.db import models
from django.urls import reverse_lazy
from easy_thumbnails.fields import ThumbnailerImageField


class Designation(BaseModel):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse_lazy("employees:designation_detail", kwargs={"pk": self.pk})

    @staticmethod
    def get_list_url():
        return reverse_lazy("employees:designation_list")

    @staticmethod
    def get_create_url():
        return reverse_lazy("employees:designation_create")

    def get_update_url(self):
        return reverse_lazy("employees:designation_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("employees:designation_delete", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

    def employee_count(self):
        return self.employee_set.filter(is_active=True).count()


class Department(BaseModel):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    department_lead = models.ForeignKey("employees.Employee", on_delete=models.PROTECT, limit_choices_to={"is_active": True}, blank=True, null=True, related_name="department_lead")

    def get_absolute_url(self):
        return reverse_lazy("employees:department_detail", kwargs={"pk": self.pk})

    @staticmethod
    def get_list_url():
        return reverse_lazy("employees:department_list")

    @staticmethod
    def get_create_url():
        return reverse_lazy("employees:department_create")

    def get_update_url(self):
        return reverse_lazy("employees:department_change", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("employees:department_delete", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

    def employee_count(self):
        return self.employee_set.filter(is_active=True).count()


class Employee(BaseModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE, null=True)
    user = models.OneToOneField("accounts.User", on_delete=models.PROTECT, limit_choices_to={"is_active": True}, related_name="employee", null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    employee_id = models.CharField(max_length=128, unique=True, null=True)
    gender = models.CharField(max_length=128, choices=GENDER_CHOICES, blank=True, null=True)
    marital_status = models.CharField(max_length=128, choices=MARITAL_CHOICES, blank=True, null=True)
    personal_email = models.EmailField(max_length=128, null=True)
    mobile = models.CharField(max_length=128, null=True)
    whatsapp = models.CharField(max_length=128, null=True)
    date_of_birth = models.DateField(null=True)
    religion = models.CharField(max_length=128, choices=RELIGION_CHOICES, blank=True, null=True)
    experience = models.TextField(null=True, blank=True)
    qualifications = models.TextField(null=True, blank=True)
    photo = ThumbnailerImageField(blank=True, null=True, upload_to="employees/photos/")

    # Company Info
    official_email = models.EmailField(max_length=128, blank=True, null=True)
    department = models.ForeignKey("employees.Department", on_delete=models.PROTECT, limit_choices_to={"is_active": True}, null=True)
    designation = models.ForeignKey("employees.Designation", on_delete=models.PROTECT, limit_choices_to={"is_active": True}, null=True)
    course = models.ForeignKey("masters.Course", on_delete=models.PROTECT, limit_choices_to={"is_active": True}, blank=True, null=True)
    is_also_tele_caller = models.CharField(max_length=128, choices=[("Yes", "Yes"), ("No", "No")], default="No")

    status = models.CharField(max_length=120, choices=EMPLOYEE_STATUS_CHOICES, default='Appointed')
    resigned_date = models.DateField(null=True, blank=True)
    notice_date = models.DateField('Notice Period Last Date', null=True, blank=True)
    resigned_form = models.FileField(null=True, blank=True, upload_to="resigned-form/")
    termination_date = models.DateField(null=True, blank=True)
    termination_reason = models.CharField(max_length=100, null=True, blank=True)

    # Parent Info
    father_name = models.CharField(max_length=128, blank=True, null=True)
    father_mobile = models.CharField(max_length=128, blank=True, null=True)
    mother_name = models.CharField(max_length=128, blank=True, null=True)
    guardian_name = models.CharField(max_length=128, blank=True, null=True)
    guardian_mobile = models.CharField(max_length=128, blank=True, null=True)
    relationship_with_employee = models.CharField("Guardian Relationship With Employee", max_length=128, blank=True, null=True)

    # Dates
    date_of_joining = models.DateField(blank=True, null=True)
    date_of_confirmation = models.DateField(blank=True, null=True)

    # Job Documents
    offer_letter = models.FileField(blank=True, null=True, upload_to="employees/doc/")
    joining_letter = models.FileField(blank=True, null=True, upload_to="employees/doc/")
    agreement_letter = models.FileField(blank=True, null=True, upload_to="employees/doc/")
    experience_letter = models.FileField(blank=True, null=True, upload_to="employees/doc/")

    # Residence Info
    type_of_residence = models.CharField(max_length=128, choices=RESIDENCE_CHOICES, blank=True, null=True)
    residence_name = models.CharField(max_length=128, blank=True, null=True)
    residential_address = models.TextField(blank=True, null=True)
    residence_contact = models.CharField(max_length=128, blank=True, null=True)
    residential_zip_code = models.CharField(max_length=128, blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    permanent_zip_code = models.CharField(max_length=128, blank=True, null=True)

    # Account Info
    bank_name = models.CharField(max_length=128, blank=True, null=True)
    account_name = models.CharField(max_length=128, blank=True, null=True)
    account_number = models.CharField("Bank Account Number", max_length=128, blank=True, null=True)
    ifsc_code = models.CharField("Bank IFSC Code", max_length=128, blank=True, null=True)
    bank_branch = models.CharField(max_length=128, blank=True, null=True)
    pan_number = models.CharField("PAN Card Number", max_length=128, blank=True, null=True)
    employment_type = models.CharField(max_length=128, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, null=True)

    # Emergency Info
    blood_group = models.CharField(max_length=128, choices=BLOOD_CHOICES, blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    other_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transportation_allowance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    def fullname(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def get_absolute_url(self):
        return reverse_lazy("employees:employee_detail", kwargs={"pk": self.pk})

    def get_image_url(self):
        if self.photo:
            return self.photo.url
        return f"https://ui-avatars.com/api/?name={self.user[:2]}&background=fdc010&color=fff&size=128"

    @staticmethod
    def get_list_url():
        return reverse_lazy("employees:employee_list")

    @staticmethod
    def get_create_url():
        return reverse_lazy("employees:employee_create")

    def get_update_url(self):
        if hasattr(self.user, 'usertype') and self.user.usertype == 'manager':
            return reverse_lazy("employees:partner_update", kwargs={'pk': self.pk})
        return reverse_lazy("employees:employee_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("employees:employee_delete", kwargs={"pk": self.pk})

    def is_hod_staff(self):
        return Department.objects.filter(department_lead=self).exists()

    def save(self, *args, **kwargs):
        if not self.pk and self.photo:
            self.photo.name = f"{uuid.uuid4()}{os.path.splitext(self.photo.name)[1]}"
        super().save(*args, **kwargs)
