from .models import AcademicYear
from branches.models import Branch
from django import forms

class HomeForm(forms.Form):
    branch = forms.ModelChoiceField(queryset=Branch.objects.filter(is_active=True))
    academic_year = forms.ModelChoiceField(queryset=AcademicYear.objects.all())
