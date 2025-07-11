import os
from core import mixins
from django.db.models import Q
from django_tables2 import RequestConfig
from django.db.models import Count
from django.core.files.storage import default_storage
from core.pdfview import PDFView
from datetime import datetime
from django.db.models import Sum
from django.conf import settings
from django.template import loader
from django.test import override_settings
from collections import defaultdict
from branches.models import Branch
from core.models import Setting
from branches.tables import BranchTable
from admission.models import Admission, Attendance, FeeReceipt, AdmissionEnquiry
from admission.tables import AdmissionEnquiryTable
from employees.models import Employee
from masters.models import Batch, Course

from .forms import HomeForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy

from core.tables import SettingsTable

# class HomeView(mixins.LoginRequiredMixin, mixins.FormView):
#     template_name = "core/home.html"
#     form_class = HomeForm
#     success_url = reverse_lazy('core:dashboard')

#     def get(self, request, *args, **kwargs):
#         user = request.user
#         if not user.is_superuser:
#             branch = user.branch
#             academic_year = HomeForm.base_fields['academic_year'].queryset.first()

#             if branch and academic_year:
#                 request.session['branch'] = branch.id
#                 request.session['academic_year'] = academic_year.id
#                 return redirect(self.success_url)

#         return super().get(request, *args, **kwargs)

#     def get_form(self, *args, **kwargs):
#         user = self.request.user
#         form = super().get_form(*args, **kwargs)
#         if not user.is_superuser:
#             form.fields['branch'].initial = user.branch
#             form.fields['branch'].queryset = form.fields['branch'].queryset.filter(id=user.branch.id)
#         return form

#     def form_valid(self, form):
#         self.request.session['branch'] = form.cleaned_data['branch'].id
#         self.request.session['academic_year'] = form.cleaned_data['academic_year'].id
#         return super().form_valid(form)


class HomeView(mixins.HybridTemplateView):
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
        
        elif user.is_superuser or user.usertype == "admin_staff":
            context["branch_count"] = Branch.objects.filter(is_active=True).count() or 0
            context["total_employee_count"] = Employee.objects.count()
            context["total_student_count"] = Admission.objects.count()
            context["total_course_count"] = Course.objects.count()

            branch_infos = Branch.objects.filter(is_active=True).annotate(
                student_count=Count("admission", distinct=True),
                employee_count=Count("employee", distinct=True),
            )

            branch_infos = list(branch_infos)

            for branch in branch_infos:
                students = Admission.objects.filter(branch=branch)

                total_pending_amount = 0
                total_fee_paid = 0

                for student in students:
                    total_paid = FeeReceipt.objects.filter(student=student).aggregate(
                        total=Sum("amount")
                    )["total"] or 0

                    total_fee_paid += total_paid

                    if student.course and student.course.fees is not None:
                        pending_amount = student.course.fees - total_paid
                        if pending_amount > 0:
                            total_pending_amount += pending_amount

                branch.pending_fee_amount = total_pending_amount
                branch.total_fee_paid = total_fee_paid

            context["branch_infos"] = branch_infos

            
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

        elif user.usertype == "sales_head":
            active_enquiries = AdmissionEnquiry.objects.filter(is_active=True)
            branch = user.branch 
            students_in_branch = Admission.objects.filter(branch=branch)

            context['my_leads'] = active_enquiries.filter(tele_caller=self.request.user.employee).count()
            context['awaiting_leads'] = active_enquiries.filter(tele_caller__isnull=True).count()
            context["assigned_lead_count"] = active_enquiries.filter(tele_caller__isnull=False).count()
            context["tele_callers_count"] = Employee.objects.filter(user__usertype="tele_caller", is_active=True).count()
            context['total_enquiries'] = active_enquiries.count()
            context['enquiry_type_counts'] = active_enquiries.values('enquiry_type').annotate(count=Count('id'))
            context['branch_counts'] = active_enquiries.values('branch__id', 'branch__name').annotate(count=Count('id'))
            context['course_counts'] = active_enquiries.values('course__id', 'course__name').annotate(count=Count('id'))
            context['status_counts'] = active_enquiries.values('status').annotate(count=Count('id'))

        elif user.usertype == "tele_caller":
            branch = user.branch 
            students_in_branch = Admission.objects.filter(branch=branch)

            today = datetime.now().date()
            today_enquiries_qs = AdmissionEnquiry.objects.filter(
                tele_caller=self.request.user.employee,
                next_enquiry_date=today
            )

            table = AdmissionEnquiryTable(today_enquiries_qs)
            RequestConfig(self.request, paginate={"per_page": 10}).configure(table)

            context['total_my_leads'] = AdmissionEnquiry.objects.filter(tele_caller=self.request.user.employee).count()
            context['awaiting_leads'] = AdmissionEnquiry.objects.filter(tele_caller__isnull=True).count()
            context["student_count"] = students_in_branch.count()
            context["employee_count"] = Employee.objects.filter(branch=branch, is_active=True).count()
            context["today_enquiries"] = today_enquiries_qs
            context["table"] = table
            context["today_date"] = datetime.now().date()
            context['branch_counts'] = AdmissionEnquiry.objects.values('branch__id', 'branch__name').annotate(count=Count('id'))
            context['course_counts'] = AdmissionEnquiry.objects.values('course__id', 'course__name').annotate(count=Count('id'))
            context['status_counts'] = AdmissionEnquiry.objects.values('status').annotate(count=Count('id'))
            context['enquiry_type_counts'] = AdmissionEnquiry.objects.values('enquiry_type').annotate(count=Count('id'))

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


class IDCardView(PDFView):
    pdfkit_options = {
        "page-height": "3.534in",
        "page-width": "1.9690in",
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        if pk:
            # If a specific PK is provided, fetch based on Admission or Employee
            try:
                self.instance = Admission.objects.get(pk=pk)
                self.template_name = "core/student_id_card.html"
            except Admission.DoesNotExist:
                self.instance = get_object_or_404(Employee, pk=pk)
                self.template_name = "core/id_card.html"
        else:
            # For logged-in user
            if request.user.usertype == "student":
                self.instance = get_object_or_404(Admission, user=request.user)
                self.template_name = "core/student_id_card.html"
            else:
                self.instance = get_object_or_404(Employee, user=request.user)
                self.template_name = "core/id_card.html"

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "ID Card"
        context["instance"] = self.instance
        return context

    def render_html(self, *args, **kwargs):
        static_url = f"{self.request.scheme}://{self.request.get_host()}{settings.STATIC_URL}"
        media_url = f"{self.request.scheme}://{self.request.get_host()}{settings.MEDIA_URL}"

        with override_settings(STATIC_URL=static_url, MEDIA_URL=media_url):
            template = loader.get_template(self.get_template_names())
            context = self.get_context_data(*args, **kwargs)
            return template.render(context)

    def get_filename(self):
        return "id_card.pdf"