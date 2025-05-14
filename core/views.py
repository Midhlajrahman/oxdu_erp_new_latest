from core import mixins
from core.pdfview import PDFView
from datetime import datetime
from django.db.models import Sum
from collections import defaultdict
from branches.models import Branch
from core.models import Setting
from branches.tables import BranchTable
from admission.models import Admission, Attendance, FeeReceipt, AdmissionEnquiry
from employees.models import Employee
from masters.models import Batch, Course

from .forms import HomeForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy

from .models import AcademicYear
from core.tables import SettingsTable


class HomeView(mixins.LoginRequiredMixin, mixins.FormView):
    template_name = "core/home.html"
    form_class = HomeForm
    success_url = reverse_lazy('core:dashboard')

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser:
            branch = user.branch
            academic_year = HomeForm.base_fields['academic_year'].queryset.first()

            if branch and academic_year:
                request.session['branch'] = branch.id
                request.session['academic_year'] = academic_year.id
                return redirect(self.success_url)

        return super().get(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        user = self.request.user
        form = super().get_form(*args, **kwargs)
        if not user.is_superuser:
            form.fields['branch'].initial = user.branch
            form.fields['branch'].queryset = form.fields['branch'].queryset.filter(id=user.branch.id)
        return form

    def form_valid(self, form):
        self.request.session['branch'] = form.cleaned_data['branch'].id
        self.request.session['academic_year'] = form.cleaned_data['academic_year'].id
        return super().form_valid(form)


class DashboardView(mixins.HybridTemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        months = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]

        if user.usertype == "student":
            try:
                admission = get_object_or_404(Admission, user=self.request.user)
                student_admission = Admission.objects.get(user=user)
                attendance_records = Attendance.objects.filter(student=student_admission, is_active=True)

                attendance_by_month = {month: {"records": [], "total_present": 0, "total_absent": 0} for month in months}

                total_present = 0
                total_absent = 0

                for record in attendance_records:
                    month_name = record.register.date.strftime("%B")
                    attendance_by_month[month_name]["records"].append(record)

                    if record.status == "Present":
                        attendance_by_month[month_name]["total_present"] += 1
                        total_present += 1
                    elif record.status == "Absent":
                        attendance_by_month[month_name]["total_absent"] += 1
                        total_absent += 1

                context["attendance_by_month"] = attendance_by_month
                context["days_in_month"] = list(range(1, 32))
                context["total_present"] = total_present
                context["total_absent"] = total_absent
                context["admission"] = admission

            except Admission.DoesNotExist:
                context["attendance_by_month"] = {}
                context["days_in_month"] = list(range(1, 32))
                context["total_present"] = 0
                context["total_absent"] = 0
                context["admission"] = admission
                
                
        elif user.usertype == "teacher":
            teacher = Employee.objects.filter(user=user).first()

            if teacher:
                student_list = Admission.objects.filter(course=teacher.course, branch=teacher.branch, is_active=True)

                attendance_by_student = {
                    student: {"records": [], "total_present": 0, "total_absent": 0} for student in student_list
                }

                student_attendance = Attendance.objects.filter(
                    student__in=student_list,
                    is_active=True,
                    register__date__month=datetime.now().month
                )

                for record in student_attendance:
                    student_key = record.student 
                    attendance_by_student[student_key]["records"].append(record)
                    
                    if record.status == "Present":
                        attendance_by_student[student_key]["total_present"] += 1
                    elif record.status == "Absent":
                        attendance_by_student[student_key]["total_absent"] += 1

                context["attendance_by_student"] = attendance_by_student
                context["days_in_month"] = list(range(1, 32))
                context["teacher_branch"] = teacher.branch
                context["teacher_course"] = teacher.course.name
                context["student_count"] = student_list.count()
                context["months"] = months
                context["batches"] = Batch.objects.all()
                context["academic_years"] = AcademicYear.objects.all()
        
        elif user.is_superuser or user.usertype == "admin_staff":
            context["branch_count"] = Branch.objects.count()
            context["total_employee_count"] = Employee.objects.count()
            context["total_student_count"] = Admission.objects.count()
            context["total_course_count"] = Course.objects.count()
            
        elif user.usertype == "branch_staff":
            branch = user.branch 

            students_in_branch = Admission.objects.filter(branch=branch)

            total_balance = sum(
                (student.course.fees - (FeeReceipt.objects.filter(student=student).aggregate(total_paid=Sum('amount'))['total_paid'] or 0))
                if student.course else 0
                for student in students_in_branch
            )
            total_credited = sum(
                FeeReceipt.objects.filter(student=student).aggregate(total_credited=Sum('amount'))['total_credited'] or 0
                for student in students_in_branch
            )

            context["branch"] = branch
            context["employee_count"] = Employee.objects.filter(branch=branch, is_active=True).count()
            context["student_count"] = students_in_branch.count()
            context["total_balance"] = total_balance
            context["total_credited"] = total_credited
            context['demo_leads'] = AdmissionEnquiry.objects.filter(status="demo").count()

        elif user.usertype == "mentor":
            branch = user.branch 
            students_in_branch = Admission.objects.filter(branch=branch)


            context["branch"] = branch
            context["employee_count"] = Employee.objects.filter(branch=branch, is_active=True).count()
            context["student_count"] = students_in_branch.count()

        elif user.usertype == "tele_caller":
            branch = user.branch 
            students_in_branch = Admission.objects.filter(branch=branch)

            context['total_my_leads'] = AdmissionEnquiry.objects.filter(tele_caller=self.request.user.employee).count()
            context['awaiting_leads'] = AdmissionEnquiry.objects.filter(tele_caller__isnull=True).count()
            context["student_count"] = students_in_branch.count()
            context["employee_count"] = Employee.objects.filter(branch=branch, is_active=True).count()

        return context
    

class Settings(mixins.HybridListView):
    model = Setting
    permissions = ("is_superuser", "admin_staff",)
    branch_filter = False
    table_class = SettingsTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Settings"
        return context

    
class SettingsDetailView(mixins.HybridDetailView):
    model = Setting
    permissions = ("admin_staff", "is_superuser",)


class SettingsCreate(mixins.HybridCreateView):
    model = Setting
    fields = ["instance_id", "access_token"]
    permissions = ("is_superuser", "admin_staff",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Settings"
        return context

    def get_success_url(self):
        return reverse_lazy('core:setting_list')

    def get_success_message(self, cleaned_data):
        return "Settings Updated Successfully"

    def form_valid(self, form):
        Setting.objects.all().delete()
        return super().form_valid(form)

    

class SettingsUpdateView(mixins.HybridUpdateView):
    model = Setting
    permissions = ("is_superuser", "admin_staff", )


class SettingsDeleteView(mixins.HybridDeleteView):
    model = Setting
    permissions = ("is_superuser", "admin_staff",)


class AcademicYearListView(mixins.HybridListView):
    model = AcademicYear
    permissions = ("branch_staff", "teacher", "admin_staff", "is_superuser")
    branch_filter = False  
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_master"] = True
        context["is_academic_year"] = True
        context["can_add"] = True
        context["new_link"] = reverse_lazy("core:academicyear_create")
        return context
    
class AcademicYearDetailView(mixins.HybridDetailView):
    model = AcademicYear
    permissions = ("branch_staff", "admin_staff", "teacher", "is_superuser",)
    

class AcademicYearCreateView(mixins.HybridCreateView):
    model = AcademicYear
    permissions = ("is_superuser", "teacher", "branch_staff", "admin_staff", )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "New Academic Year"
        return context

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
    

class AcademicYearUpdateView(mixins.HybridUpdateView):
    model = AcademicYear
    permissions = ("is_superuser", "teacher", "branch_staff", "admin_staff", )


class AcademicYearDeleteView(mixins.HybridDeleteView):
    model = AcademicYear
    permissions = ("is_superuser", "teacher", "branch_staff", "admin_staff",)


class IDCardView(PDFView):
    template_name = 'core/id_card.html'
    pdfkit_options = {
        "page-height": "3.5433in",
        "page-width": "1.9685in",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.usertype == "student":
            instance = get_object_or_404(Admission, user=self.request.user)
        else:
            instance = get_object_or_404(Employee, user=self.request.user)
        context["title"] = "Registration"
        context["instance"] = instance
        return context
    
    def get_filename(self):
        return "id_card.pdf"