from .models import AcademicYear
from branches.models import Branch
from django import forms

class HomeForm(forms.Form):
    branch = forms.ModelChoiceField(queryset=Branch.objects.filter(is_active=True))
    academic_year = forms.ModelChoiceField(queryset=AcademicYear.objects.all())


class AcademicYearForm(forms.ModelForm):

    class Meta:
        model = AcademicYear
        fields = ('start_month_session', "start_year_session", "end_month_session", "end_year_session",)  
        