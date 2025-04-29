from core.base import BaseForm
from core.models import AcademicYear
from branches.models import Branch

from .models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginForm(AuthenticationForm):
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(), required=True, label="Academic Year", empty_label="Select Academic Year", widget=forms.Select(attrs={'class': 'form-control'})
    )

    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), required=True, label="Branch", empty_label="Select Branch", widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        fields = ['academic_year', 'branch', 'username', 'password']


class UserForm(BaseForm):
    class Meta:
        model = User
        fields = ("email", "usertype", "password")
