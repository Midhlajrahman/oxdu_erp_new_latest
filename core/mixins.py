import operator
import re
from functools import reduce

from core.models import AcademicYear
from branches.models import Branch

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import OneToOneField
from django.db.models import Q
from django.db.models import CharField
from django.db.models import TextField
from django.forms import ModelChoiceField
from django.forms import ModelMultipleChoiceField
from django.forms import models as model_forms
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import NoReverseMatch
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django_filters.views import FilterView
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin
from django_tables2 import Table
from django_tables2 import columns
from django_filters import FilterSet
from django_filters import ModelChoiceFilter
from django_filters import ModelMultipleChoiceFilter

def convert_to_spaces(text):
    result = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return result


def check_access(request, permissions):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.usertype in permissions:
            return True
    return False

class CustomLoginRequiredMixin(LoginRequiredMixin):
    permissions = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # if (
        #     (usertype == 'student' and not Student.objects.filter(user=self.request.user).exists())
        #     or (usertype == 'parent' and not Parent.objects.filter(user=self.request.user).exists())
        #     or not Employee.objects.filter(user=self.request.user).exists()
        # ):
        #     return self.handle_no_permission()

        if self.permissions and not check_access(request, self.permissions):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

class AcademicYearBranchSessionMixin:
    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect(reverse_lazy("auth_login"))

        academic_year = request.session.get('academic_year')
        branch = request.session.get('branch')

        # Redirect to core:home with a message if academic_year or branch is missing
        if not academic_year or not branch:
            messages.warning(request, "Please select an academic year and branch to proceed.")
            return redirect(reverse_lazy("core:home"))

        # Proceed with the original dispatch method
        return super().dispatch(request, *args, **kwargs)


class CustomModelFormMixin:
    exclude = None

    # Rewriting get_form_class to support exclude attribute
    def get_form_class(self):
        model = getattr(self, "model", None)
        if self.exclude:
            exclude = getattr(self, "exclude", None)
            return model_forms.modelform_factory(model, exclude=exclude)
        return super().get_form_class()


class HybridDetailView(AcademicYearBranchSessionMixin, CustomLoginRequiredMixin, DetailView,):
    template_name = "app/common/object_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['can_change'] = True
        context['can_delete'] = True
        context["title"] = self.get_object().__str__
        return context


class HybridCreateView(AcademicYearBranchSessionMixin, CustomLoginRequiredMixin, CustomModelFormMixin, SuccessMessageMixin, CreateView):
    exclude = ("creator","branch")
    template_name = "app/common/object_form.html"
    academic_year_field = "academic_year"
    branch_field = "branch"
    inline_formset = None

    def get_success_url(self):
        try:
            return self.object.get_list_url()
        except NoReverseMatch:
            return None

    def form_valid(self, form):
        form.instance.creator = self.request.user

        for field in [self.academic_year_field, self.branch_field]:
            if hasattr(form.instance, field):
                setattr(form.instance, field, getattr(self, f'get_{field}')())

        response = super().form_valid(form)

        if self.inline_formset:
            formset = self.get_context_data().get('formset')
            if formset and formset.is_valid():
                formset.instance = self.object
                formset.save()

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            object_data = model_to_dict(self.object)
            object_data.setdefault('name', str(self.object))
            return JsonResponse({'success': True, 'result': object_data})

        return response

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print(form.errors)
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)
        
    def get_success_message(self, cleaned_data):
        if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            instance = self.object
            success_message = f"{self.model.__name__} '{instance}' was Created successfully. "
            success_message += f"<a href='{instance.get_absolute_url()}'>View {self.model.__name__}</a>."
            return success_message
        return

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New " + convert_to_spaces(self.model.__name__)
        context["sub_title"] = convert_to_spaces(self.model.__name__) + " Form"
        context['formset'] =self.inline_formset(self.request.POST or None) if self.inline_formset else None
        return context

    def get_form(self, form_class=None):
        # Get the form class (either passed or automatically generated)
        form = super().get_form(form_class)
        # Filter ForeignKey, OneToOneField, and ManyToManyField to only show active objects
        for field_name, field in form.fields.items():
            if isinstance(field, (ModelChoiceField, ModelMultipleChoiceField)):
                model_field = self.model._meta.get_field(field_name)
                if isinstance(model_field, (ForeignKey, OneToOneField, ManyToManyField)):
                    # Limit queryset to only active objects
                    related_model = model_field.remote_field.model
                    active_objects = related_model.objects.filter(is_active=True)
                    field.queryset = active_objects
        return form

    def get_academic_year(self):
        academic_year_id = self.request.session.get('academic_year')
        loged_academic_year = AcademicYear.objects.filter(id=academic_year_id).first() if academic_year_id else None
        return loged_academic_year

    def get_branch(self):
        branch_id = self.request.session.get('branch')
        loged_branch = Branch.objects.filter(id=branch_id).first() if branch_id else None
        return loged_branch


class HybridUpdateView(AcademicYearBranchSessionMixin, CustomLoginRequiredMixin, CustomModelFormMixin, SuccessMessageMixin, UpdateView):
    exclude = ("creator","branch")
    template_name = "app/common/object_form.html"
    inline_formset = None

    def get_success_message(self, cleaned_data):
        instance = self.object
        success_message = f"{self.model.__name__} '{instance}' was Updated successfully. "
        success_message += f"<a href='{instance.get_absolute_url()}'>View {self.model.__name__}</a>."
        return success_message

    def get_success_url(self):
        redirect_url = self.request.session.get('current_view_url')
        if redirect_url:
            return redirect_url
        return self.object.get_list_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update " + convert_to_spaces(self.model.__name__)
        context["sub_title"] = convert_to_spaces(self.model.__name__) + " Form"
        context['formset'] =self.inline_formset(self.request.POST or None,instance=self.object) if self.inline_formset else None
        return context

    def form_valid(self,form):
        response = super().form_valid(form)
        if self.inline_formset:
            formset = self.get_context_data().get('formset')
            if formset and formset.is_valid():
                formset.instance = self.object
                formset.save()
        return response

    def get_branch(self):
        return Branch.objects.filter(id=self.request.session.get('branch')).first()


class HybridDeleteView(AcademicYearBranchSessionMixin, CustomLoginRequiredMixin, DeleteView,):
    template_name = "app/common/confirm_delete.html"

    def get_success_url(self):
        return self.object.get_list_url()


class HybridListView(AcademicYearBranchSessionMixin, CustomLoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView, ListView):
    template_name = "app/common/object_list.html"
    table_pagination = {"per_page": 50}
    branch_filter = True
    branch_field_name = 'branch'
    search_fields = []  # Set dynamically
    
    def setup_search_fields(self):
        """Dynamically sets search_fields to all CharField and TextField in the model."""
        if not self.search_fields:
            self.search_fields = [
                field.name for field in self.model._meta.fields 
                if isinstance(field, (CharField, TextField))
            ]

    def get(self, request, *args, **kwargs):
        # Store the current URL in the session
        request.session['current_view_url'] = request.build_absolute_uri()
        # Update table_pagination based on query params
        per_page = request.GET.get("table_pagination")
        if per_page and per_page.isdigit():
            self.table_pagination = {"per_page": int(per_page)}
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        branch_id = self.request.session.get('branch')
        if self.branch_filter and branch_id:
            branch = Branch.objects.get(id=branch_id)
            queryset = queryset.filter(**{self.branch_field_name: branch})
        # Apply search filter dynamically
        self.setup_search_fields()
        search_fields = getattr(self, "search_fields", None)
        if search_fields:
            query = self.request.GET.get("q")
            if query:
                q_list = [Q(**{f"{field}__icontains": query}) for field in search_fields]
                queryset = queryset.filter(reduce(operator.or_, q_list))
        try:
            queryset.filter(is_active=True)
            return queryset.filter(is_active=True)
        except FieldError:
            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.model._meta.verbose_name_plural
        context[f"is_{self.model.__name__.lower()}"] = True
        context["can_add"] = True
        try:
            new_link = self.model.get_create_url()
        except AttributeError:
            new_link = None
        context["new_link"] = new_link

        
        return context
    
    def get_table_class(self):
        if self.table_class:
            return self.table_class
        """Dynamically generates a table class including all model fields except the excluded ones and adds an 'action' column."""
        exclude_fields = {"is_active", "creator", "updated", "id", "created"}  

        # Get model fields and exclude unwanted fields
        included_fields = [field.name for field in self.model._meta.fields if field.name not in exclude_fields]

        class DynamicTable(Table):
            action = columns.TemplateColumn(
                template_name="app/partials/table_actions.html", 
                orderable=False
            )

            class Meta:
                model = self.model
                attrs = {"class": "table table-vcenter text-nowrap table-bordered border-bottom"}  # Set table attributes
                fields = included_fields  # Use only allowed fields

        return DynamicTable


    

class HybridFormView(AcademicYearBranchSessionMixin, CustomLoginRequiredMixin, FormView):
    pass


class HybridTemplateView(AcademicYearBranchSessionMixin, CustomLoginRequiredMixin, TemplateView):
    template_name = "app/common/object_view.html"


class HybridView(AcademicYearBranchSessionMixin, CustomLoginRequiredMixin, View):
    pass


class OpenView(AcademicYearBranchSessionMixin, TemplateView):
    pass
