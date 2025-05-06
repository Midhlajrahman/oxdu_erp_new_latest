from core.base import BaseModel

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Branch(BaseModel):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    manager_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    opening_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_address(self):
        parts = [self.city, self.district, self.state, self.country, self.postal_code]
        return ', '.join(filter(None, parts))

    class Meta(BaseModel.Meta):
        verbose_name_plural = "Branches"

 