from django.db.models import Q
from django.shortcuts import render
from core import mixins
from core.utils import build_url
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


from . import forms
from . import tables
from .functions import generate_employee_id
from .models import Department
from .models import Designation
from .models import Employee
from branches.models import Branch


class DepartmentListView(mixins.HybridListView):
    model = Department
    table_class = tables.DepartmentTable
    filterset_fields = {"name": ["icontains"]}
    permissions = ("branch_staff", "admin_staff")
    branch_filter = False
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_master'] = True
        context["is_department"] = True
        return context


class DepartmentDetailView(mixins.HybridDetailView):
    model = Department
    permissions = ("branch_staff", "admin_staff")
    branch_filter = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_delete"] = mixins.check_access(self.request, ("branch_staff"))
        return context


class DepartmentCreateView(mixins.HybridCreateView):
    model = Department
    permissions = ("branch_staff", "admin_staff")
    branch_filter = False


class DepartmentUpdateView(mixins.HybridUpdateView):
    model = Department
    permissions = ("branch_staff", "admin_staff")
    branch_filter = False


class DepartmentDeleteView(mixins.HybridDeleteView):
    model = Department
    permissions = ("branch_staff", "admin_staff")
    branch_filter = False


class DesignationListView(mixins.HybridListView):
    model = Designation
    table_class = tables.DesignationTable
    branch_filter = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_master'] = True
        context["is_designation"] = True
        return context


class DesignationDetailView(mixins.HybridDetailView):
    model = Designation


class DesignationCreateView(mixins.HybridCreateView):
    model = Designation


class DesignationUpdateView(mixins.HybridUpdateView):
    model = Designation


class DesignationDeleteView(mixins.HybridDeleteView):
    model = Designation


class ProfileView(mixins.HybridView):
    template_name = "employees/profile.html"

    def get(self, request, *args, **kwargs):
        context = {"title": "Profile", "is_profile": True, "employee": Employee.objects.get(user=self.request.user), "photo_form": forms.EmployeePhotoForm()}

        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = forms.EmployeePhotoForm(request.POST or None, request.FILES or None, instance=self.request.user.employee)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": True})
        return JsonResponse({"status": False})


class EmployeeListView(mixins.HybridListView):
    model = Employee
    table_class = tables.EmployeeTable
    permissions = ("branch_staff", "admin_staff")
    filterset_fields = {'branch': ['exact'] ,'department': ['exact'], 'designation': ['exact'], 'gender': ['exact'],}
    search_fields = ("user__email", "employee_id", "first_name", "middle_name", "last_name", "marital_status", "mobile", "whatsapp")
    
    def get_queryset(self):
        user = self.request.user 
        
        if user.is_superuser:
            return Employee.objects.filter(is_active=True) 
        
        elif hasattr(user, "usertype") and user.usertype == "branch_staff":
            employee = Employee.objects.filter(user=user).first()
            if employee and employee.branch:
                return Employee.objects.filter(branch=employee.branch, is_active=True)
        
        return Employee.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_employee"] = True
        return context

    
class TeleCallerListView(mixins.HybridListView):
    model = Employee
    table_class = tables.EmployeeTable
    permissions = ("branch_staff", "admin_staff", "sales_head")
    filterset_fields = {'branch': ['exact'] ,'department': ['exact'], 'designation': ['exact'], 'gender': ['exact'],}
    search_fields = ("user__email", "employee_id", "first_name", "middle_name", "last_name", "marital_status", "mobile", "whatsapp")
    branch_filter = False
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = Employee.objects.filter(user__usertype="tele_caller", is_active=True)

        return queryset
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = Employee.objects.filter(
            Q(user__usertype="tele_caller") | Q(is_also_tele_caller="Yes"),
            is_active=True
        )
        return queryset
    


class EmployeeDetailView(mixins.HybridDetailView):
    queryset = Employee.objects.filter(is_active=True)
    template_name = "employees/profile.html"
    permissions = ("branch_staff", "admin_staff")

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["can_change"] = has_access(self, "EmployeeCreateView")
    #     context["can_delete"] = has_access(self, "EmployeeUpdateView")
    #     context["form"] = forms.EmployeeDependentForm()
    #     context["employee_skill_form"] = forms.EmployeeSkillForm()
    #     context["employee_education_form"] = forms.EmployeeEducationForm()
    #     context["job_history_form"] = forms.JobHistoryForm()
    #     context["employee_document_form"] = forms.EmployeeDocumentForm()
    #     context["medical_history_form"] = forms.MedicalHistoryForm()
    #     context["salary_setup_form"] = forms.SalarySetupForm()
    #     context["employee_transfer_form"] = forms.EmployeeTransferForm()
    #     return context


class EmployeeCreateView(mixins.HybridCreateView):
    model = Employee
    form_class = forms.EmployeePersonalDataForm
    permissions = ("branch_staff", "admin_staff")
    template_name = "employees/employee_form.html"
    exclude = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_hrm"] = True
        context["is_personal"] = True
        context["is_create"] = True
        context["subtitle"] = "Personal Data"
        return context

    def get_success_url(self):
        if "save_and_next" in self.request.POST:
            url = build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'parent'})
            return url
        return build_url("employees:employee_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        user = form.save(commit=False)

        if form.cleaned_data.get("password"):
            user.set_password(form.cleaned_data["password"])

        branch = None
        if self.request.user.is_authenticated and hasattr(self.request.user, "branch") and self.request.user.branch:
            branch = self.request.user.branch
        else:
            branch = Branch.objects.first()

        if not branch:
            form.add_error(None, "No branch assigned and no default branch available.")
            return self.form_invalid(form)

        user.branch = branch

        pk = self.kwargs.get("pk")
        if pk:
            employee = get_object_or_404(Employee, pk=pk)
            user.first_name = employee.first_name
            user.last_name = employee.last_name or ""
            user.save()

            employee.user = user
            employee.branch = user.branch
            employee.usertype = user.usertype
            employee.photo = user.image
            employee.save()
        else:
            user.save()

        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return "Employee Personal Data Created Successfully"


class EmployeeUpdateView(mixins.HybridUpdateView):
    model = Employee
    permissions = ("branch_staff", "admin_staff")
    template_name = "employees/employee_form.html"

    def get_initial(self):
        initial = super().get_initial()
        info_type = self.request.GET.get("type", "personal")
        if info_type == "official" and not self.object.employee_id:
            initial['employee_id'] = generate_employee_id()
        return initial

    def get_form_class(self):
        form_classes = {
            "parent": forms.EmployeeParentDataForm,
            "address": forms.EmployeeAddressDataForm,
            "official": forms.EmployeeOfficialDataForm,
            "financial": forms.EmployeeFinancialDataForm,
            "personal": forms.EmployeePersonalDataForm,  # Default case
        }
        info_type = self.request.GET.get("type", "personal")
        return form_classes.get(info_type, forms.EmployeePersonalDataForm)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info_type = self.request.GET.get("type", "personal")
        subtitles = {"parent": "Parent Data", "address": "Address Data", "official": "Official Data", "financial": "Financial Data", "personal": "Personal Data"}
        urls = {
            "personal": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'personal'}),
            "parent": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'parent'}),
            "address": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'address'}),
            "official": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'official'}),
            "financial": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'financial'}),
        }
        context["title"] = "Edit Employee"
        context["subtitle"] = subtitles.get(info_type, "Personal Data")
        context['info_type_urls'] = urls
        context[f"is_{info_type}"] = True
        context["is_update"] = True
        context["is_hrm"] = True
        context['department_form'] = forms.DepartmentForm(self.request.POST or None)
        context['designation_form'] = forms.DesignationForm(self.request.POST or None)
        context['course_form'] = forms.CourseForm(self.request.POST or None)
        return context

    def get_success_url(self):
        if "save_and_next" in self.request.POST:
            info_type = self.request.GET.get("type", "personal")
            if info_type == "financial" and self.object.user:
                next_url = build_url("accounts:user_update", kwargs={"pk": self.object.user.pk})
            else:
                urls = {
                    "personal": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'parent'}),
                    "parent": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'address'}),
                    "address": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'official'}),
                    "official": build_url("employees:employee_update", kwargs={"pk": self.object.pk}, query_params={'type': 'financial'}),
                    "financial": build_url("accounts:user_create", kwargs={"pk": self.object.pk}, query_params={'type': 'parent'}),
                }
                next_url = urls.get(info_type, build_url("employee_detail", kwargs={"pk": self.object.pk}))
            return next_url
        return self.object.get_list_url()

    def get_success_message(self, cleaned_data):
        info_type = self.request.GET.get("type", "personal")
        messages_dict = {
            "personal": "Personal data updated successfully.",
            "parent": "Parent data updated successfully.",
            "address": "Address data updated successfully.",
            "official": "Official data updated successfully.",
            "financial": "Financial data updated successfully.",
        }
        return messages_dict.get(info_type, "Data updated successfully.")


class EmployeeDeleteView(mixins.HybridDeleteView):
    model = Employee
    permissions = ("branch_staff", "admin_staff")
