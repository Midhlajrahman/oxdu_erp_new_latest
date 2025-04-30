from core.base import BaseForm
from django.forms import modelformset_factory
from django import forms
from django.forms import inlineformset_factory

from .models import ComplaintRegistration, Course, PDFBookResource, PdfBook, Syllabus


class PdfBookForm(forms.ModelForm):
    class Meta:
        model = PdfBook
        fields = ('name', "pdf")
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'pdf': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
        }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['DELETE'] = forms.BooleanField(required=False)


PdfBookFormSet = inlineformset_factory(
    PDFBookResource,
    PdfBook,
    form=PdfBookForm,
    extra=1,
    can_delete=True,  
)

class CourseSelectionForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.filter(is_active=True))
    


class SyllabusForm(forms.ModelForm):
    class Meta:
        model = Syllabus
        exclude = ['id',]
        fields = ['course', 'title', 'description', 'week']
        widgets = {
            "course": forms.HiddenInput(),
            "week": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError('This field cannot be blank.')
        return title

SyllabusFormSet = modelformset_factory(Syllabus, form=SyllabusForm, extra=1, can_delete=True)


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = ComplaintRegistration
        fields = ['complaint_type', "complaint", "status", ]