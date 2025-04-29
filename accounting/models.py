from core.base import BaseModel
from core.choices import ACCOUNTING_MASTER_CHOICES
from core.choices import MAIN_GROUP_CHOICES
from core.choices import OPENING_BALANCE_TYPE_CHOICES

from django.db import models
from django.urls import reverse_lazy


class GroupMaster(BaseModel):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=100)
    nature_of_group = models.CharField(max_length=30, choices=ACCOUNTING_MASTER_CHOICES)
    main_group = models.CharField(max_length=30, choices=MAIN_GROUP_CHOICES)
    is_locked = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_list_url():
        return reverse_lazy("accounting:group_master_list")

    @staticmethod
    def get_create_url():
        return reverse_lazy("accounting:group_master_create")

    def get_absolute_url(self):
        return reverse_lazy("accounting:group_master_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse_lazy("accounting:group_master_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("accounting:group_master_delete", kwargs={"pk": self.pk})


class Account(BaseModel):
    name = models.CharField(max_length=100)
    under = models.ForeignKey(GroupMaster, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)

    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    opening_balance_type = models.CharField(max_length=5, choices=OPENING_BALANCE_TYPE_CHOICES, null=True, blank=True)
    limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_days = models.PositiveIntegerField(null=True, blank=True)
    alias_name = models.CharField(max_length=150, null=True, blank=True)
    # address
    address_line1 = models.CharField(max_length=150, null=True, blank=True)
    address_line2 = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    pin_code = models.PositiveBigIntegerField(null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)
    phone_no_off = models.CharField("Phone No. (Off)", max_length=50, null=True, blank=True)
    phone_no_res = models.CharField("Phone No. (Res)", max_length=50, null=True, blank=True)
    mobile_no = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    contact_person = models.CharField(max_length=128, null=True, blank=True)
    fax_no = models.CharField(max_length=128, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        if self.alias_name:
            return self.alias_name
        return self.name

    @staticmethod
    def get_list_url():
        return reverse_lazy("accounting:account_list")

    @staticmethod
    def get_create_url():
        return reverse_lazy("accounting:account_create")

    def get_absolute_url(self):
        return reverse_lazy("accounting:account_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse_lazy("accounting:account_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("accounting:account_delete", kwargs={"pk": self.pk})
