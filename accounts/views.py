from core import mixins
from core.utils import build_url
from employees.models import Employee
from admission.models import Admission

from . import tables
from .forms import CustomLoginForm
from .forms import UserForm
from .models import User
from django.contrib.auth.views import LoginView
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = CustomLoginForm

    def form_valid(self, form):
        super().form_valid(form)
        academic_year = form.cleaned_data.get('academic_year')
        branch = form.cleaned_data.get('branch')
        self.request.session['academic_year'] = academic_year.id
        self.request.session['branch'] = branch.id
        return HttpResponseRedirect(self.get_success_url())


class UserListView(mixins.HybridListView):
    model = User
    table_class = tables.UserTable
    filterset_fields = ("is_active", "is_staff")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Users"
        context["can_add"] = True
        context["new_link"] = reverse_lazy("accounts:user_create")
        return context


class UserDetailView(mixins.HybridDetailView):
    model = User


class UserCreateView(mixins.HybridCreateView):
    model = User
    form_class = UserForm
    permissions = ("manager", "admin_staff")
    exclude = None

    def get_template_names(self):
        if "pk" in self.kwargs:
            return "employees/employee_form.html"
        return super().get_template_names()

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        if "pk" in self.kwargs:
            employee = get_object_or_404(Employee, pk=self.kwargs["pk"])
            form.fields['email'].initial = employee.personal_email if employee.personal_email else None
        return form

    def form_valid(self, form):
        # Hash the password before saving the user
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])

        pk = self.kwargs.get("pk")  # Get employee primary key safely
        if pk:
            employee = get_object_or_404(Employee, pk=pk)
            user.first_name = employee.first_name
            user.last_name = employee.last_name or ""

            user.save()  # Save the user after setting password
            employee.user = user  # Link the employee to the user
            employee.user.usertype = 'teacher'
            employee.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        urls = {
            "personal": build_url("employees:employee_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'personal'}),
            "parent": build_url("employees:employee_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'parent'}),
            "address": build_url("employees:employee_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'address'}),
            "official": build_url("employees:employee_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'official'}),
            "financial": build_url("employees:employee_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'financial'}),
            "account": build_url("accounts:user_create", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'account'}),
        }
        context['info_type_urls'] = urls
        context['title'] = 'New Employee'
        context['subtitle'] = 'Account Details'
        context['is_account'] = True
        if "pk" in self.kwargs:
            context['object'] = get_object_or_404(Employee, pk=self.kwargs["pk"])
        return context

    def get_success_url(self):
        return Employee.get_list_url()

    def get_success_message(self, cleaned_data):
        message = "Employee created successfully"
        return message


class StudentUserCreateView(mixins.HybridCreateView):
    model = User
    form_class = UserForm
    permissions = ("manager", "admin_staff")
    exclude = None

    def get_template_names(self):
        if "pk" in self.kwargs:
            return "admission/admission_form.html"
        return super().get_template_names()

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        if "pk" in self.kwargs:
            student = get_object_or_404(Admission, pk=self.kwargs["pk"])
            form.fields['email'].initial = student.personal_email if student.personal_email else None
        return form

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])

        pk = self.kwargs.get("pk")  
        if pk:
            student = get_object_or_404(Admission, pk=pk)
            user.first_name = student.first_name
            user.last_name = student.last_name or ""

            user.save()
            student.user = user 
            student.user.usertype = 'student'
            student.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        urls = {
            "personal": build_url("admission:admission_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'personal'}),
            "parent": build_url("admission:admission_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'parent'}),
            "address": build_url("admission:admission_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'address'}),
            "official": build_url("admission:admission_update", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'official'}),
            "account": build_url("accounts:student_user_create", kwargs={"pk": self.kwargs.get('pk')}, query_params={'type': 'account'}),
        }
        context['info_type_urls'] = urls
        context['title'] = 'New Admission'
        context['subtitle'] = 'Account Details'
        context['is_account'] = True
        if "pk" in self.kwargs:
            context['object'] = get_object_or_404(Admission, pk=self.kwargs["pk"])
        return context

    def get_success_url(self):
        return Admission.get_list_url()

    def get_success_message(self, cleaned_data):
        message = "Admission created successfully"
        return message


class StudentUserUpdateView(mixins.HybridUpdateView):
    model = User
    exclude = None
    fields = ("email", "usertype")
    template_name = "admission/admission_form.html"
    permissions = ("manager", "admin_staff")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit Admission"
        context['subtitle'] = "Account Form"
        urls = {
            "personal": build_url("admission:admission_update", kwargs={"pk": self.object.student.pk}, query_params={'type': 'personal'}),
            "parent": build_url("admission:admission_update", kwargs={"pk": self.object.student.pk}, query_params={'type': 'parent'}),
            "address": build_url("admission:admission_update", kwargs={"pk": self.object.student.pk}, query_params={'type': 'address'}),
            "official": build_url("admission:admission_update", kwargs={"pk": self.object.student.pk}, query_params={'type': 'official'}),
            "financial": build_url("admission:admission_update", kwargs={"pk": self.object.student.pk}, query_params={'type': 'financial'}),
        }
        context['info_type_urls'] = urls
        context['is_account'] = True
        return context

    def get_success_url(self):
        return reverse_lazy("admission:admission_list")
    

class UserUpdateView(mixins.HybridUpdateView):
    model = User
    exclude = None
    fields = ("email", "usertype")
    template_name = "employees/employee_form.html"
    permissions = ("manager", "admin_staff")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit Employee"
        context['subtitle'] = "Account Form"
        urls = {
            "personal": build_url("employees:employee_update", kwargs={"pk": self.object.employee.pk}, query_params={'type': 'personal'}),
            "parent": build_url("employees:employee_update", kwargs={"pk": self.object.employee.pk}, query_params={'type': 'parent'}),
            "address": build_url("employees:employee_update", kwargs={"pk": self.object.employee.pk}, query_params={'type': 'address'}),
            "official": build_url("employees:employee_update", kwargs={"pk": self.object.employee.pk}, query_params={'type': 'official'}),
            "financial": build_url("employees:employee_update", kwargs={"pk": self.object.employee.pk}, query_params={'type': 'financial'}),
        }
        context['info_type_urls'] = urls
        context['is_account'] = True
        return context

    def get_success_url(self):
        return reverse_lazy("employees:employee_list")


class UserDeleteView(mixins.HybridDeleteView):
    model = User
