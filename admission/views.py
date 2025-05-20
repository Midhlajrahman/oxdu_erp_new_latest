import datetime
import openpyxl
import csv
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse

from django.shortcuts import get_object_or_404

from django.views import View
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from django.contrib.auth import get_user_model

from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction

from django.urls import reverse_lazy
from django.urls import reverse

from django.forms import formset_factory, inlineformset_factory
from core.utils import build_url
from core import mixins

from admission .models import Admission, Attendance, AttendanceRegister, FeeReceipt, AdmissionEnquiry
from masters.models import Batch, Course
from masters.forms import BatchForm
from employees.models import Employee
from branches.models import Branch
from core.pdfview import PDFView

from . import tables
from . import forms

from admission.forms import AttendanceForm, AttendanceUpdateForm, FeeReceiptFormSet, AdmissionEnquiryForm
# from .forms import AdmissionForm


User = get_user_model()

@require_POST
@csrf_protect
def change_status(request, pk):
    admission = get_object_or_404(Admission, pk=pk)
    new_status = request.POST.get("is_active")

    if new_status == "True":
        admission.is_active = True
        if admission.user:
            admission.user.is_active = True
            admission.user.save()
    elif new_status == "False":
        admission.is_active = False
        if admission.user:
            admission.user.is_active = False
            admission.user.save()

    admission.save()
    return redirect(request.META.get("HTTP_REFERER", "/"))


def get_batches_for_course(request):
    course_id = request.GET.get('course_id')
    branch = request.GET.get('branch') 
    
    if not course_id:
        return JsonResponse({'error': 'Course ID is required'}, status=400)

    course = get_object_or_404(Course, id=course_id)

    if request.user.is_superuser:
        user_branch = request.session.get('branch')
    else:
        user_branch = request.user.branch

    if not user_branch and branch:
        user_branch = branch

    if not user_branch:
        return JsonResponse({'error': 'User branch not found or selected branch missing'}, status=400)

    batches = Batch.objects.filter(course=course, branch=user_branch)

    data = [{'id': batch.id, 'name': batch.batch_name} for batch in batches]

    return JsonResponse({'batches': data})



class ImportEnquiryView(View):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            messages.error(request, "No file uploaded.")
            return redirect('admission:public_lead_list')

        try:
            if file.name.endswith('.xlsx'):
                wb = openpyxl.load_workbook(file)
                sheet = wb.active
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    phone = row[0] if len(row) > 0 else None
                    full_name = row[1] if len(row) > 1 else None
                    city = row[2] if len(row) > 2 else None

                    if phone:
                        AdmissionEnquiry.objects.create(
                            contact_number=phone,
                            full_name=full_name,
                            city=city,
                        )

            elif file.name.endswith('.csv'):
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                next(reader, None)  # Skip header
                for row in reader:
                    full_name = row[0] if len(row) > 0 else None
                    city = row[1] if len(row) > 1 else None
                    phone = row[2] if len(row) > 2 else None

                    if phone:
                        AdmissionEnquiry.objects.create(
                            contact_number=phone,
                            full_name=full_name,
                            city=city,
                        )

            else:
                messages.error(request, "Unsupported file type. Please upload .xlsx or .csv.")
                return redirect('admission:public_lead_list')

            messages.success(request, "Leads imported successfully.")
        except Exception as e:
            messages.error(request, f"Import failed: {e}")

        return redirect('admission:public_lead_list')

    
def add_to_me(request, pk):
    enquiry = get_object_or_404(AdmissionEnquiry, pk=pk)

    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "You are not registered as an employee.")
        return redirect('admission:public_lead_list')

    if enquiry.tele_caller is None:
        enquiry.tele_caller = employee
        enquiry.save()
        messages.success(request, "You have been assigned to this enquiry.")
    else:
        messages.warning(request, "This enquiry already has a tele-caller.")
        
    return redirect('admission:public_lead_list')


def student_check_data(request):
    personal_email = request.GET.get('personal_email')
    student = AdmissionEnquiry.objects.filter(personal_email=personal_email).first()

    if student:
        return JsonResponse({
            'status': True,
            'student_name': student.full_name,
            'student_id': student.pk,
            'full_name': student.full_name,
            'date_of_birth': student.date_of_birth.strftime('%d/%m/%Y') if student.date_of_birth else None,
            'religion': student.religion,
            'city': student.city,
            'district': student.district,
            'state': student.state,
            'pin_code': student.pin_code,
            'personal_email': student.personal_email,
            'contact_number': student.contact_number,
            'whatsapp_number': student.whatsapp_number,
            'parent_full_name': student.parent_full_name,
            'parent_contact_number': student.parent_contact_number,
            'parent_whatsapp_number': student.parent_whatsapp_number,
            'parent_mail_id': student.parent_mail_id,
            # 'photo': student.photo.url if student.photo else None,  # Only if needed
        })
    else:
        return JsonResponse({'status': False})


class AdmissionListView(mixins.HybridListView):
    model = Admission
    table_class = tables.AdmissionTable
    filterset_fields = {'course': ['exact'], "branch": ['exact'], "batch": ['exact'], "admission_number": ['exact'], "admission_date": ['exact']}
    permissions = ("branch_staff", "teacher", "admin_staff", "is_superuser", "mentor",)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        user = self.request.user
        if user.usertype == "teacher":
            queryset = queryset.filter(branch=user.branch, course=user.employee.course)

        elif user.usertype == "branch_staff":
            queryset = queryset.filter(branch=user.branch)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Students"
        context["is_admission"] = True
        context["is_students"] = True
        context["can_add"] = self.request.user.usertype in ["is_superuser", "branch_staff"]
        context["new_link"] = reverse_lazy("admission:admission_create")
        return context
    

class InactiveAdmissionListView(mixins.HybridListView):
    model = Admission
    table_class = tables.AdmissionTable
    filterset_fields = {
        'course': ['exact'],
        'branch': ['exact'],
        'batch': ['exact'],
        'admission_number': ['exact'],
        'admission_date': ['exact'],
    }
    permissions = ("branch_staff", "teacher", "admin_staff", "is_superuser", "mentor", )

    def get_queryset(self):
        queryset = Admission.objects.filter(is_active=False)
        user = self.request.user
        if user.usertype == "teacher":
            queryset = queryset.filter(
                branch=user.branch,
                course=user.employee.course,
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Inactive Students"
        context["is_admission"] = True
        context["is_inactive_students"] = True
        context["can_add"] = False
        return context
    

class AdmissionDetailView(mixins.HybridDetailView):
    queryset = Admission.objects.all()
    template_name = "admission/profile.html"
    permissions = ("branch_staff", "teacher", "admin_staff", "is_superuser", "mentor")


class AdmissionCreateView(mixins.HybridCreateView):
    model = Admission
    form_class = forms.AdmissionPersonalDataForm
    permissions = ("branch_staff", "teacher", "admin_staff", "is_superuser")
    template_name = "admission/admission_form.html"
    exclude = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admission"] = True
        context["is_personal"] = True
        context["is_create"] = True
        context["subtitle"] = "Personal Data"
        return context

    def get_success_url(self):
        if "save_and_next" in self.request.POST:
            url = build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'parent'})
            return url
        return build_url("admission:admission_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        branch_id = self.request.session.get('branch')
        print('branch_id=',branch_id)
        form.instance.creator = self.request.user
        form.instance.branch = Branch.objects.get(pk=branch_id)
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return "Admission Personal Data Created Successfully"


class AdmissionUpdateView(mixins.HybridUpdateView):
    model = Admission
    permissions = ("branch_staff", "admin_staff", "mentor", "is_superuser")
    template_name = "admission/admission_form.html"

    def get_form_class(self):
        form_classes = {
            "parent": forms.AdmissionParentDataForm,
            "address": forms.AdmissionAddressDataForm,
            "official": forms.AdmissionOfficialDataForm,
            "personal": forms.AdmissionPersonalDataForm,  
            "financial": forms.AdmissionFinancialDataForm
        }
        info_type = self.request.GET.get("type", "personal")
        return form_classes.get(info_type, forms.AdmissionPersonalDataForm)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info_type = self.request.GET.get("type", "personal")
        subtitles = {"parent": "Parent Data", "address": "Address Data", "official": "Official Data", "financial": "Financial Data",  "personal": "Personal Data"}
        urls = {
            "personal": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'personal'}),
            "parent": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'parent'}),
            "address": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'address'}),
            "official": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'official'}),
            "financial": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'financial'}),
        }
        context["title"] = "Edit Admission"
        context["subtitle"] = subtitles.get(info_type, "Personal Data")
        context['info_type_urls'] = urls
        context[f"is_{info_type}"] = True
        context["is_admission"] = True
        context['batch_form'] = BatchForm(self.request.POST or None)
        return context

    def get_success_url(self):
        if "save_and_next" in self.request.POST:
            info_type = self.request.GET.get("type", "personal")
            if info_type == "official" and self.object.user:
                next_url = build_url("accounts:student_user_update", kwargs={"pk": self.object.user.pk})
            else:
                urls = {
                    "personal": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'parent'}),
                    "parent": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'address'}),
                    "address": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'official'}),
                    "official": build_url("admission:admission_update", kwargs={"pk": self.object.pk}, query_params={'type': 'financial'}),
                    "financial": build_url("accounts:student_user_create", kwargs={"pk": self.object.pk}, query_params={'type': 'parent'}),
                }
                next_url = urls.get(info_type, build_url("admission_detail", kwargs={"pk": self.object.pk}))
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


class AdmissionDeleteView(mixins.HybridDeleteView):
    model = Admission
    permissions = ("is_superuser", "teacher", "branch_staff", )


class PublicLeadListView(mixins.HybridListView):
    template_name = "admission/enquiry/list.html"
    model = AdmissionEnquiry
    table_class = tables.PublicEnquiryListTable
    filterset_fields = {'city': ['exact'], 'branch': ['exact'], 'date': ['exact']}
    permissions = ("branch_staff", "admin_staff", "is_superuser", "tele_caller")
    branch_filter = False

    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        table.request = self.request 
        return table

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(tele_caller__isnull=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Public Leads"
        context["is_lead"] = True
        context["is_public_lead"] = True  
        user_type = self.request.user.usertype
        context["can_add"] = user_type in ("tele_caller",)
        context["new_link"] = reverse_lazy("admission:admission_enquiry_create")    
        return context


class MyleadListView(mixins.HybridListView):
    model = AdmissionEnquiry
    table_class = tables.AdmissionEnquiryTable
    filterset_fields = {'course': ['exact'], 'branch': ['exact'],'status': ['exact'],'date': ['exact']}
    permissions = ("branch_staff", "admin_staff", "is_superuser", "tele_caller", "mentor")
    branch_filter = False

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(tele_caller=user.employee)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_type = self.request.user.usertype

        context.update({
            "title": "My Leads",
            "is_my_lead": True,
            "can_add": user_type in ("tele_caller",),
            "new_link": reverse_lazy("admission:admission_enquiry_create"),
        })

        return context
    
class AdmissionEnquiryView(mixins.HybridListView):
    model = AdmissionEnquiry
    table_class = tables.AdmissionEnquiryTable
    filterset_fields = {'course': ['exact'], 'branch': ['exact'],'status': ['exact'],'date': ['exact']}
    permissions = ("branch_staff", "admin_staff", "is_superuser", "tele_caller", "mentor")
    branch_filter = False

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.usertype in ["branch_staff", "mentor"]:
            queryset = queryset.filter(status="demo")
        elif user.usertype == "tele_caller":
            queryset = queryset.filter(tele_caller=user.employee)
        elif user.usertype == "admin_staff" or user.is_superuser:
            queryset = queryset.filter(tele_caller__isnull=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_type = self.request.user.usertype

        context.update({
            "title": "Leads",
            "is_admission": True,
            "is_enquiry": True,
            "can_add": user_type in ("tele_caller",),
            "new_link": reverse_lazy("admission:admission_enquiry_create"),
        })

        return context
    

class AdmissionEnquiryDetailView(mixins.HybridDetailView):
    model = AdmissionEnquiry
    permissions = ("branch_staff", "tele_caller", "admin_staff", "is_superuser")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lead Details"
        return context
    

class AdmissionEnquiryCreateView(mixins.HybridCreateView):
    model = AdmissionEnquiry
    permissions = ("branch_staff", "tele_caller", "admin_staff", "is_superuser")
    exclude = ('tele_caller',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admission"] = True
        context["is_enquiry"] = True  
        context["is_create"] = True
        context["title"] = "New Lead"
        return context

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, "employee") and user.usertype == "tele_caller":
            form.instance.tele_caller = user.employee
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_list_url()


class AdmissionEnquiryUpdateView(mixins.HybridUpdateView):
    model = AdmissionEnquiry
    permissions = ("branch_staff", "tele_caller", "admin_staff", "is_superuser")
    exclude = ('tele_caller',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admission"] = True
        context["is_enquiry"] = True  
        context["title"] = "Edit Lead"
        return context

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, "employee") and user.usertype == "tele_caller":
            if not form.instance.tele_caller:
                form.instance.tele_caller = user.employee
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_list_url()
    

class AdmissionEnquiryDeleteView(mixins.HybridDeleteView):
    model = AdmissionEnquiry
    permissions = ("branch_staff", "tele_caller", "admin_staff", "is_superuser")


class DeleteUnassignedLeadsView(View):
    def post(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            count, _ = AdmissionEnquiry.objects.filter(tele_caller__isnull=True).delete()
            return JsonResponse({'message': f'{count} unassigned leads deleted successfully.'})
        return JsonResponse({'error': 'Invalid request'}, status=400)


class AttendanceRegisterListView(mixins.HybridListView):
    model = AttendanceRegister
    table_class = tables.AttendanceRegisterTable 
    filterset_fields = {'batch': ['exact'],'date': ['exact'], 'course': ['exact']}  
    permissions = ("")
    template_name = 'admission/attendance/list.html'
    
    def get_queryset(self):
        user = self.request.user
        branch = self.request.session.get('branch', getattr(user, 'branch', None))

        if user.usertype == 'admin_staff' or user.is_superuser:
            return AttendanceRegister.objects.filter(branch=branch)

        elif user.usertype == 'teacher':
            if hasattr(user, 'employee'):
                employee = user.employee
                teacher_courses = Course.objects.filter(employee=employee)
                if teacher_courses.exists():
                    return AttendanceRegister.objects.filter(branch=branch, course__in=teacher_courses)
        
        return AttendanceRegister.objects.filter(branch=branch)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.usertype == 'teacher':
            context["batches"] = Batch.objects.filter(is_active=True, course=self.request.user.employee.course, branch=self.request.user.branch)
        else:
            context["batches"] = Batch.objects.filter(is_active=True, branch=self.request.user.branch)
        context["title"] = "Attendance"
        context['is_admission'] = True
        context["is_attendance"] = True  
        context['is_batch_attendance'] = True
        user_type = self.request.user.usertype
        context["can_add"] = user_type in ("teacher",)
        return context
    
    
class AttendanceRegisterDetailView(mixins.HybridDetailView):
    model = AttendanceRegister
    permissions = ()
    template_name = "admission/attendance/object_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Attendance Register Details"
        return context
    
    
class AttendanceRegisterCreateView(mixins.HybridCreateView):
    model = AttendanceRegister
    permissions = ()
    form_class = forms.AttendanceRegisterForm
    template_name = "admission/attendance/object_form.html"

    def get_form(self):
        form = self.form_class(**self.get_form_kwargs())
        form.fields['date'].initial = datetime.date.today()

        user = self.request.user

        if user.usertype == 'teacher':
            try:
                employee = user.employee  
                teacher_courses = form.fields['course'].queryset.filter(employee=employee)

                if teacher_courses.exists():
                    form.fields['course'].queryset = teacher_courses
                    form.fields['course'].initial = teacher_courses.first()  
            except AttributeError:
                pass
        else:
            form.fields['course'].queryset = form.fields['course'].queryset.filter(is_active=True)

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch = Batch.objects.get(pk=self.kwargs['pk'])
        context["batch"] = batch
        context["title"] = f"{batch.batch_name} Attendance"

        user = self.request.user
        course_id = self.request.GET.get('course')

        if user.usertype == 'teacher':
            try:
                employee = user.employee
                teacher_courses = Course.objects.filter(employee=employee)
                context["teacher_courses"] = teacher_courses 

                if teacher_courses.exists() and not course_id:
                    course_id = teacher_courses.first().id 

            except AttributeError:
                context["teacher_courses"] = None
        
        if hasattr(user, 'branch'):
            students = Admission.objects.filter(is_active=True, batch=batch, branch=user.branch)
        else:
            students = Admission.objects.filter(is_active=True, batch=batch)
        
        if course_id:
            students = students.filter(course_id=course_id)

        initial_data = [{'student_name': student, 'student_pk': student.id, 'status': 'Present'} for student in students]

        AttendanceFormSet = formset_factory(AttendanceForm, extra=0)

        if self.request.POST:
            context['attendance_formset'] = AttendanceFormSet(self.request.POST)
        else:
            context['attendance_formset'] = AttendanceFormSet(initial=initial_data)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        attendance_formset = context['attendance_formset']
        
        batch = Batch.objects.get(pk=self.kwargs['pk'])
        branch = batch.branch  
        date = form.cleaned_data.get('date')

        if AttendanceRegister.objects.filter(batch=batch, date=date, is_active=True).exists():
            form.add_error(None, "Attendance for this batch on this date already exists.")
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                form.instance.batch = batch
                form.instance.branch = branch  
                data = form.save()

                if attendance_formset.is_valid():
                    for attendance_form in attendance_formset:
                        student_pk = attendance_form.cleaned_data.get('student_pk')
                        student = Admission.objects.get(pk=student_pk)
                        form_data = attendance_form.save(commit=False)
                        form_data.student = student
                        form_data.register = data
                        form_data.save()
                else:
                    # Print formset errors for debugging
                    print("Attendance formset errors:", attendance_formset.errors)
                    context['formset_errors'] = attendance_formset.errors
                    return render(self.request, self.template_name, context)

        except IntegrityError:
            form.add_error(None, "Attendance for this batch on this date already exists.")
            return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        batch = Batch.objects.get(pk=self.kwargs['pk'])
        kwargs['batch'] = batch
        return kwargs
    
    def get_success_url(self):
        return reverse('admission:attendance_register_list')
    

class AttendanceRegisterUpdateView(mixins.HybridUpdateView):
    model = AttendanceRegister
    permissions = ("administration", "teacher", "accounting_staff", "finance", "worker", "hrm")
    exclude = ("batch", "branch", "course",)
    template_name = "admission/attendance/object_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Attendance Register"

        # Fetch the attendance register instance and its batch
        attendance_register = self.object
        batch = attendance_register.batch
        students = Admission.objects.filter(is_active=True, batch=batch)

        # Fetch attendance records for this register
        attendance_queryset = Attendance.objects.filter(register=attendance_register)

        # Define the formset factory
        AttendanceUpdateFormSet = inlineformset_factory(
            AttendanceRegister, Attendance, form=AttendanceUpdateForm, extra=0, can_delete=True
        )

        if self.request.POST:
            context['attendance_formset'] = AttendanceUpdateFormSet(
                self.request.POST, instance=attendance_register
            )
        else:
            if attendance_queryset.exists():
                # If attendance records exist, use them
                context["attendance_formset"] = AttendanceUpdateFormSet(instance=attendance_register)
            else:
                # If no attendance records exist, create an initial dataset with students
                initial_data = [
                    {"student": student, "register": attendance_register, "status": "Present"}
                    for student in students
                ]
                context["attendance_formset"] = AttendanceUpdateFormSet(initial=initial_data, instance=attendance_register)

        # Ensure students are available in context
        context["students"] = students
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        attendance_formset = context['attendance_formset']
        self.object = form.save()
        if attendance_formset.is_valid():
            attendance_formset.instance = self.object  
            attendance_formset.save()
            
        else:
            print('attendance_formset=',attendance_formset.errors)
            return render(self.request, self.template_name, context)
        return super().form_valid(form)
    

class AttendanceRegisterDeleteView(mixins.HybridDeleteView):
    permissions = ("administration", "teacher", "accounting_staff", "finance", "worker", "hrm")  
    model = AttendanceRegister


class FeeReceiptListView(mixins.HybridListView):
    model = FeeReceipt
    table_class = tables.FeeReceiptTable
    filterset_fields = {'student': ['exact'], 'date': ['exact'], 'receipt_no': ['exact'], 'payment_type': ['exact']}
    permissions = ("branch_staff", "teacher", "admin_staff" "is_superuser", "student")
    branch_filter = False
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        user = self.request.user
        get_branch = self.request.session.get('branch')

        if user.usertype == "student":
            student_admissions = Admission.objects.filter(user=user)
            queryset = queryset.filter(student__in=student_admissions)
            
        elif user.usertype == "teacher":
            queryset = queryset.filter(student__branch=user.branch, student__course=user.employee.course)
            
        elif user.usertype == "branch_staff":
            queryset = queryset.filter(student__branch=user.branch)

        else :
            queryset = queryset.filter(student__branch=get_branch)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admission"] = True
        context["fee_reciept"] = True
        user = self.request.user
        context["can_add"] = user.usertype in ["teacher", "branch_staff", "admin_staff"]
        if context["can_add"]:
            context["new_link"] = reverse_lazy("admission:feereceipt_create")
        return context

    
class FeeReceiptDetailView(mixins.HybridDetailView):
    model = FeeReceipt
    template_name = "admission/fee_receipt/receipt_view.html"
    permissions = ("branch_staff", "teacher", "is_superuser", "student")
    

class FeeReceiptCreateView(mixins.HybridCreateView):
    model = FeeReceipt
    fields = ["student", "receipt_no", "date", "note", "payment_type", "amount"]
    permissions = ("is_superuser", "teacher", "branch_staff")
    template_name = "admission/fee_receipt/object_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "New Fee Receipt"
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user

        if user.usertype == "teacher":
            try:
                teacher = Employee.objects.get(user=user)

                form.fields["student"].queryset = Admission.objects.filter(
                    course=teacher.course, branch=teacher.branch
                )

            except Employee.DoesNotExist:
                form.fields["student"].queryset = Admission.objects.none()

        return form

    def form_valid(self, form):
        fee_receipt = form.save(commit=False)
        fee_receipt.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form Errors:", form.errors)
        return super().form_invalid(form)
    

class FeeReceiptUpdateView(mixins.HybridUpdateView):
    model = FeeReceipt
    permissions = ("is_superuser", "teacher", "branch_staff", )


class FeeReceiptDeleteView(mixins.HybridDeleteView):
    model = FeeReceipt
    permissions = ("is_superuser", "teacher", "branch_staff", )
    

class StudentFeeOverviewListView(mixins.HybridListView):
    model = Admission
    table_class = tables.StudentFeeOverviewTable
    filterset_fields = {'branch': ['exact'], 'course': ['exact'], 'batch': ['exact'], }
    permissions = ("branch_staff", "teacher", "admin_staff", "is_superuser", "student")
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        user = self.request.user
        
        if user.usertype == "teacher":
            employee = getattr(user, "employee", None)
            if employee and employee.course:
                queryset = queryset.filter(branch=user.branch, course=employee.course)

        elif user.usertype == "branch_staff":
            queryset = queryset.filter(branch=user.branch)

        return queryset
    
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        context['title'] = "Student Receipt Overview"
        context["can_add"] = False
        context["is_admission"] = True
        context["fee_overview"] = True
        return context
    

class StudentFeeOverviewDetailView(mixins.HybridDetailView):
    model = Admission
    template_name = "admission/fee_receipt/student_fee_overview.html"
    permissions = ("branch_staff", "teacher", "is_superuser", "student")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admission = self.get_object()
        context["fee_receipts"] = admission.feereceipt_set.all()  
        return context
    

class FeeOverviewListView(mixins.HybridListView):
    model = Admission
    filterset_fields = {'branch': ['exact'], 'course': ['exact'], 'batch': ['exact']}
    permissions = ("branch_staff", "teacher", "admin_staff", "is_superuser", "student")
    template_name = "admission/fee_receipt/fee_overview.html"
    branch_filter = False
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.usertype == "student":
            queryset = queryset.filter(user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admissions = self.get_queryset()

        # Calculate total fee amount and balance across all admissions
        total_fee_amount = sum(admission.get_total_fee_amount() for admission in admissions)
        balance_amount = sum(admission.get_balance_amount() for admission in admissions)

        context["fee_receipts"] = FeeReceipt.objects.filter(student__in=admissions)
        context["total_fee_amount"] = total_fee_amount
        context["balance_amount"] = balance_amount
        return context
    

class RegistrationView(mixins.FormView):
    template_name = 'admission/registration_form.html'
    form_class = forms.RegistrationForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Registration"   
        return context

    def form_valid(self, form):
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("personal_email")

        if not password or not email:
            form.add_error("password", "Password is required.")
            form.add_error("personal_email", "Email is required.")
            return self.form_invalid(form)

        admission = form.save(commit=False)

        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=admission.first_name,
                last_name=admission.last_name,
                branch=admission.branch, 
                is_active = False,
                usertype="student", 
            )

            admission.user = user

        admission.save()
        
        self.admission_pk = admission.pk  

        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid:", form.errors)
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('admission:terms_condition', kwargs={'pk': self.admission_pk})
    
    
class TermsConditionView(View):
    template_name = "admission/terms_condition.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Terms and Conditions"   
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"pk": self.kwargs.get("pk")})

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        return redirect(reverse("admission:registration_detail", kwargs={"pk": pk}))
    

class RegistrationDetailView(PDFView):
    template_name = 'admission/registration_pdf.html'
    pdfkit_options = {
        "page-height": 297,
        "page-width": 210,
        "encoding": "UTF-8",
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Admission, pk=self.kwargs["pk"])
        context["title"] = "Registration"
        context["instance"] = instance
        return context
    
    def get_filename(self):
        return "registration_form.pdf"