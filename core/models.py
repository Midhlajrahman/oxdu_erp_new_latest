from core.choices import MODULE_CHOICES
from core.choices import MONTH_CHOICES
from core.choices import VIEW_TYPE_CHOICES
from core.choices import YEAR_CHOICES

from .base import BaseModel
from django.db import models
from django.urls import reverse_lazy


def get_default_document_settings():
    return {
        "invoice": {
            "airline": {"prefix": "AI", "start_count": 1},
            "hotel": {"prefix": "HT", "start_count": 1},
            "visa": {"prefix": "VI", "start_count": 1},
            "miscellaneous": {"prefix": "MS", "start_count": 1},
            "transportation": {"prefix": "TR", "start_count": 1},
            "package": {"prefix": "PI", "start_count": 1},
        },
        "purchase": {
            "airline": {"prefix": "PA", "start_count": 1},
            "hotel": {"prefix": "PH", "start_count": 1},
            "visa": {"prefix": "PV", "start_count": 1},
            "miscellaneous": {"prefix": "PM", "start_count": 1},
            "transportation": {"prefix": "PT", "start_count": 1},
            "package": {"prefix": "PP", "start_count": 1},
        },
        "estimate": {
            "airline": {"prefix": "QTAI", "start_count": 1},
            "hotel": {"prefix": "QTHT", "start_count": 1},
            "visa": {"prefix": "QTVI", "start_count": 1},
            "miscellaneous": {"prefix": "QTMS", "start_count": 1},
            "transportation": {"prefix": "QTTR", "start_count": 1},
            "package": {"prefix": "QTPI", "start_count": 1},
        },
        "receipt": {"prefix": "RCPT", "start_count": 1},
        "payment": {"prefix": "PY", "start_count": 1},
        "jv": {"prefix": "JV", "start_count": 1},
    }


class Setting(BaseModel):
    branch = models.OneToOneField('branches.Branch', on_delete=models.CASCADE)
    document_settings = models.JSONField(default=get_default_document_settings, help_text="Stores prefixes and start counts for invoices and purchases.")

    def __str__(self):
        return str(self.branch)

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"


class AcademicYear(BaseModel):
    start_month_session = models.CharField(max_length=10, choices=MONTH_CHOICES)
    start_year_session = models.PositiveIntegerField(choices=YEAR_CHOICES)
    end_month_session = models.CharField(max_length=10, choices=MONTH_CHOICES)
    end_year_session = models.PositiveIntegerField(choices=YEAR_CHOICES)

    class Meta:
        unique_together = ("start_month_session", "start_year_session")
        ordering = ("-start_year_session", "-start_month_session")
        
    @staticmethod
    def get_list_url():
        return reverse_lazy("core:academicyear_list")

    def get_absolute_url(self):
        return reverse_lazy("core:academicyear_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse_lazy("core:academicyear_update", kwargs={"pk": self.pk})
    
    def get_delete_url(self):
        return reverse_lazy("core:academicyear_delete", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.get_start_month_session_display()} {self.start_year_session} - {self.get_end_month_session_display()} {self.end_year_session}"

    def display(self):
        return f"{self.start_year_session[2:]}-{self.end_year_session[2:]}"


class LockingGroup(models.Model):
    GROUP_CHOICES = [
        ('SUNDRY_DEBTORS', 'Sundry Debtors'),
        ('SUNDRY_CREDITORS', 'Sundry Creditors'),
        ('INDIRECT_EXPENSE', 'Indirect Expense'),
        ('BANK_ACCOUNT', 'Bank Account'),
        ('CASH_ACCOUNT', 'Cash Account'),
    ]

    name = models.CharField(max_length=50, choices=GROUP_CHOICES, unique=True)
    group = models.OneToOneField("accounting.GroupMaster", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class LockingAccount(models.Model):
    ACCOUNT_CHOICES = [
        ('airline_rcvd_ia', 'Air-Line RCVD [IA]'),
        ('airline_rcvd_da', 'Air-Line RCVD [DA]'),
        ('hotel_rcvd', 'Hotel RCVD'),
        ('visa_rcvd', 'Visa RCVD'),
        ('miscellaneous_rcvd', 'Miscellaneous RCVD'),
        ('transportation_rcvd', 'Transportation RCVD'),
        ('package_rcvd', 'Package RCVD'),
        ('airline_paid_ia', 'Air-Line PAID [IA]'),
        ('airline_paid_da', 'Air-Line PAID [DA]'),
        ('hotel_paid', 'Hotel PAID'),
        ('visa_paid', 'Visa PAID'),
        ('miscellaneous_paid', 'Miscellaneous PAID'),
        ('transportation_paid', 'Transportation PAID'),
        ('package_paid', 'Package PAID'),
        ('CGST', 'CGST'),
        ('SGST', 'SGST'),
        ('round_off', 'Round Off'),
        ('cash_account', 'Cash Account'),
    ]
    name = models.CharField(max_length=50, choices=ACCOUNT_CHOICES, unique=True)
    account = models.OneToOneField("accounting.Account", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Link(models.Model):
    """
    A model representing a link, which can be displayed in the application.
    """

    value = models.CharField("Title", max_length=200, blank=True, null=True)
    description = models.CharField(max_length=200)
    module = models.CharField(max_length=200, choices=MODULE_CHOICES)
    view = models.CharField(max_length=200)
    name = models.CharField(max_length=200, unique=True)
    view_type = models.CharField(max_length=200, choices=VIEW_TYPE_CHOICES)
    is_dashboard_link = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_quick_access = models.BooleanField(default=False)
    created = models.DateTimeField(db_index=True, auto_now_add=True)

    employee_access = models.BooleanField(default=True)
    admin_staff_access = models.BooleanField(default=False)

    class Meta:
        ordering = ("view",)

    def gen_link(self):
        name = self.name.split(".")
        if self.view_type in ["CreateView", "DashboardView", "ListView", "TemplateView", "View"]:
            try:
                return reverse_lazy(f"{name[0]}:{name[1]}") if len(name) == 2 else reverse_lazy(f"{name[0]}")
            except:
                return ""
        return ""

    def __str__(self):
        return str(self.view)