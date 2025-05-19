from core.base import BaseForm
from django.forms import modelformset_factory
from django import forms
from django.forms import inlineformset_factory

from .models import ComplaintRegistration, Course, PDFBookResource, PdfBook, Syllabus, ChatSession, Update, PlacementRequest, Batch


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


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatSession
        fields = ['message']


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ["title", "description", "image"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter update title"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter update description",
                "rows": 5
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control-file"
            }),
        }

    
class PlacementRequestForm(forms.ModelForm):
    class Meta:
        model = PlacementRequest
        fields = ["student", "resume", "portfolio_link", "behance_link", "experience"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].disabled = True

    
class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ["course", "batch_name", "description", "starting_time", "ending_time", "starting_date", "ending_date",]