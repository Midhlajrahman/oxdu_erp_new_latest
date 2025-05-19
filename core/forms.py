from branches.models import Branch
from django import forms

class HomeForm(forms.Form):
    branch = forms.ModelChoiceField(queryset=Branch.objects.filter(is_active=True))