import datetime
import json
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.forms import formset_factory, inlineformset_factory

from django.db import IntegrityError

from django.db import transaction
from django.urls import reverse_lazy
from core import mixins
from admission.models import Admission
from employees.models import Employee

from . import forms
from . import tables
from .forms import PdfBookFormSet, SyllabusForm,SyllabusFormSet
from .models import Batch, ComplaintRegistration, Course, PDFBookResource, PdfBook, Syllabus, BatchSyllabusStatus


@csrf_exempt
def status_update(request, pk):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

    try:
        print("DEBUG: Is user authenticated?", request.user.is_authenticated)
        print("DEBUG: User:", request.user)
        print("DEBUG: Usertype attribute exists?", hasattr(request.user, 'usertype'))
        if hasattr(request.user, 'usertype'):
            print("DEBUG: Usertype:", request.user.usertype)

        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "User not authenticated"}, status=403)

        data = json.loads(request.body)
        status_value = data.get("status", "pending")

        syllabus = get_object_or_404(Syllabus, pk=pk)

        if hasattr(request.user, 'usertype') and request.user.usertype == 'student':
            admission = Admission.objects.filter(user=request.user).first()
            if not admission or not admission.batch:
                return JsonResponse({"status": "error", "message": "Valid batch not found for the student"}, status=404)
            batch = admission.batch
        elif hasattr(request.user, 'usertype') and request.user.usertype == 'teacher':
            teacher = Employee.objects.filter(user=request.user).first()
            if teacher and teacher.course:
                batch = Batch.objects.filter(course=teacher.course).first()
                if not batch:
                    return JsonResponse({"status": "error", "message": "Batch not found for the teacher's course"}, status=404)
            else:
                return JsonResponse({"status": "error", "message": "Teacher's course not found"}, status=404)
        else:
            return JsonResponse({"status": "error", "message": "Unauthorized user type"}, status=403)

        bss, created = BatchSyllabusStatus.objects.get_or_create(
            syllabus=syllabus,
            user=request.user,
            batch=batch,
            defaults={'status': status_value}
        )

        if not created:
            bss.status = status_value
            bss.save()

        if status_value == 'completed':
            syllabus.is_completed = True
            syllabus.save()

        return JsonResponse({"status": "success", "created": created}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    except Exception as e:
        print("EXCEPTION:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def student_syllabus_redirect(request):
    if request.user.is_authenticated and request.user.usertype == "student":
        admission = Admission.objects.filter(user=request.user).first()
        if admission and admission.course:
            return redirect("masters:syllabus_detail", course_id=admission.course.id)
    return redirect("core:home")



class BatchListView(mixins.HybridListView):
    model = Batch
    table_class = tables.BatchTable
    filterset_fields = {'academic_year': ['exact'], }
    permissions = ("branch_manager", "teacher", "admin_staff" "is_superuser")
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_master"] = True
        context["is_batch"] = True
        return context
    

    
class BatchDetailView(mixins.HybridDetailView):
    model = Batch
    permissions = ("branch_staff", "teacher", "is_superuser",)
    

class BatchCreateView(mixins.HybridCreateView):
    model = Batch
    permissions = ("is_superuser", "teacher", "branch_staff", )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "New Batch"
        return context

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
    

class BatchUpdateView(mixins.HybridUpdateView):
    model = Batch
    permissions = ("is_superuser", "teacher", "branch_staff", )


class BatchDeleteView(mixins.HybridDeleteView):
    model = Batch
    permissions = ("is_superuser", "teacher", "branch_staff", )
    

class CourseListView(mixins.HybridListView):
    model = Course
    table_class = tables.CourseTable
    filterset_fields = {'name': ['exact'], }
    permissions = ("branch_manager", "teacher", "admin_staff" "is_superuser")
    branch_filter = False
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_course"] = True 
        context["is_master"] = True
        return context
    

    
class CourseDetailView(mixins.HybridDetailView):
    model = Course
    permissions = ("branch_staff", "teacher", "is_superuser",)
    

class CourseCreateView(mixins.HybridCreateView):
    model = Course
    permissions = ("is_superuser", "teacher", "branch_staff", )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "New Course"
        return context

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
    

class CourseUpdateView(mixins.HybridUpdateView):
    model = Course
    permissions = ("is_superuser", "teacher", "branch_staff", )


class CourseDeleteView(mixins.HybridDeleteView):
    model = Course
    permissions = ("is_superuser", "teacher", "branch_staff", )


class PDFBookResourceListView(mixins.HybridListView):
    model = PDFBookResource
    table_class = tables.PDFBookResourceTable
    filterset_fields = ('course',)
    permissions = ("superadmin",'manager','teacher', "student")
    branch_filter = False
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.usertype == "teacher":
            try:
                teacher = Employee.objects.get(user=user)
                queryset = queryset.filter(course=teacher.course)
            except Employee.DoesNotExist:
                queryset = PDFBookResource.objects.none() 

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "PDF Resource List"
        context["is_pdf_resource"] = True
        context["is_master"] = True
        context["can_add"] = True
        context["new_link"] = reverse_lazy("masters:pdfbook_resource_create")
        return context


class PDFBookResourceDetailView(mixins.HybridDetailView):
    model = PDFBookResource
    template_name = "masters/pdfbook/object_view.html"
    permissions = ("superadmin", "manager", "teacher", "student")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.get_object()

        pdfbook_entries = PdfBook.objects.filter(resource=resource, is_active=True)

        context["customer_table"] = tables.PDFBookResourceTable(pdfbook_entries)
        context["pdfbook_entries"] = pdfbook_entries 
        return context


class PDFBookResourceCreateView(mixins.HybridCreateView):
    model = PDFBookResource
    permissions = ("superadmin", "manager", "teacher")
    exclude = ("is_active",)
    template_name = "masters/pdfbook/object_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user

        if user.usertype == "teacher":
            try:
                teacher = Employee.objects.get(user=user)
                form.fields["course"].queryset = Course.objects.filter(id=teacher.course.id)
                form.initial["course"] = teacher.course 
            except Employee.DoesNotExist:
                form.fields["course"].queryset = Course.objects.none() 

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["pdfbook_formset"] = PdfBookFormSet(self.request.POST, self.request.FILES)
        else:
            context["pdfbook_formset"] = PdfBookFormSet()
        context["title"] = "Create PDF Book"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pdfbook_formset = PdfBookFormSet(self.request.POST, self.request.FILES)

        with transaction.atomic():
            self.object = form.save()
            pdfbook_formset.instance = self.object

            if pdfbook_formset.is_valid():
                pdfbook_formset.save()
            else:
                print("\nFormset Errors:")
                for form in pdfbook_formset:
                    if form.errors:
                        print(form.errors.as_json())
                print("\nNon-Form Errors:", pdfbook_formset.non_form_errors())
                return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        return render(self.request, self.template_name, context)


class PDFBookResourceUpdateView(mixins.HybridUpdateView):
    model = PDFBookResource
    permissions = ("superadmin", "manager", "teacher")
    template_name = "masters/pdfbook/object_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pdfbook_instance = self.get_object() 

        formset_queryset = PdfBook.objects.filter(resource=pdfbook_instance, is_active=True)

        if self.request.POST:
            context['pdfbook_formset'] = PdfBookFormSet(self.request.POST, self.request.FILES, instance=pdfbook_instance, queryset=formset_queryset)
        else:
            context['pdfbook_formset'] = PdfBookFormSet(instance=pdfbook_instance, queryset=formset_queryset)

        context["title"] = "Update PDF Book"
        context["is_pdfbook"] = True
        return context
   
    def form_valid(self, form):
        
        self.object = form.save()
        
        pdfbook_formset = PdfBookFormSet(self.request.POST, self.request.FILES, instance=self.object)
        
        pdfbook_formset.instance = self.object

        if pdfbook_formset.is_valid():
            PdfBook.objects.filter(resource=self.object).delete()
            for f in pdfbook_formset:
                f.instance.resource = self.object
                f.save()
                print('create')
            # pdfbook_formset.save()
            return super().form_valid(form)
        else:
            print("\nFormset Errors:")
            for form in pdfbook_formset:
                if form.errors:
                    print(form.errors.as_json())
            print("\nNon-Form Errors:", pdfbook_formset.non_form_errors())

            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        return render(self.request, self.template_name, context)
    

class PDFBookResourceDeleteView(mixins.HybridDeleteView):
    model = PDFBookResource
    permissions = ("superadmin",'manager','driver')
    

class PDFBookListView(mixins.HybridListView):
    model = PdfBook
    table_class = tables.PdfBookTable
    filterset_fields = ('name',)
    permissions = ("superadmin",'manager','teacher', "student")
    branch_filter = False
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        user = self.request.user

        if user.usertype == "student":
            student_courses = Admission.objects.filter(user=user).values_list("course", flat=True)
            
            queryset = queryset.filter(resource__course__in=student_courses)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "PDF Book List"
        context["is_pdf_book"] = True
        user = self.request.user
        context["can_add"] = user.usertype == "teacher" and getattr(user, "branch_staff", False)
        context["new_link"] = reverse_lazy("masters:pdfbook_resource_create")
        return context


class SyllabusListView(mixins.HybridListView):
    model = Batch
    table_class = tables.SyllabusBatchTable
    filterset_fields = {'batch_name': ['exact']}
    permissions = ("teacher", "admin_staff", "branch_staff", "student")
    template_name = 'masters/syllabus/list.html'
    branch_filter = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["courses"] = Course.objects.filter(is_active=True)
        context["title"] = "Batches"
        context['is_masters'] = True
        context["is_syllabus"] = True
        context["can_add"] = user.usertype  != "student"
        context["new_link"] = reverse_lazy("masters:pdfbook_resource_create")
        return context
    

class SyllabusDetailView(TemplateView):
    template_name = "masters/syllabus/object_view.html"
    permissions = ()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_pk = self.kwargs.get("pk")
        course = get_object_or_404(Course, pk=course_pk)
        user = self.request.user
        syllabus_ids = Syllabus.objects.filter(course=course).values_list('id', flat=True)
        completed_statuses = BatchSyllabusStatus.objects.filter(
            syllabus_id__in=syllabus_ids,
            user=user
        )
        print("status==",completed_statuses)
        completed_statuses_ids = completed_statuses.values_list('syllabus_id', flat=True)
        
        pending_statuses = Syllabus.objects.filter(is_active=True).exclude(id__in=completed_statuses_ids)

        context["title"] = f"Syllabus - {course.name}"
        context["course"] = course
        context["pending_items"] = pending_statuses
        context["completed_items"] = completed_statuses
        return context


class SyllabusCreateView(mixins.HybridCreateView):
    model = Syllabus
    template_name = "masters/syllabus/object_form.html"
    permissions = ("teacher", "admin_staff", "branch_staff", "student")
    exclude = ("is_active",)

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=self.kwargs.get("course_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = kwargs
        context["title"] = "Syllabus"
        context["is_masters"] = True
        context["is_syllabus"] = True
        context["course"] = self.course
        return context

    def get(self, request, *args, **kwargs):
        formset = SyllabusFormSet(queryset=Syllabus.objects.none())
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset = SyllabusFormSet(request.POST)

        for form in formset:
            form.data = form.data.copy()
            form.data[form.add_prefix('course')] = str(self.course.id)

        if formset.is_valid():
            for syllabus_form in formset:
                if syllabus_form.cleaned_data and not syllabus_form.cleaned_data.get("DELETE", False):
                    syllabus_item = syllabus_form.save(commit=False)
                    syllabus_item.course = self.course
                    syllabus_item.save()
            formset.save()
            return redirect("masters:syllabus_list")
        else:
            print("Formset errors:", formset.errors)
            return self.form_invalid(formset)

    def form_invalid(self, formset):
        context = self.get_context_data(formset=formset)
        context['formset_errors'] = formset.errors
        return self.render_to_response(context)



class SyllabusUpdateView(View):
    template_name = "masters/syllabus/object_form.html"
    permissions = ("teacher", "admin_staff", "branch_staff", "student")
    
    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=self.kwargs.get("course_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = kwargs
        context["title"] = "Syllabus"
        context["is_masters"] = True
        context["is_syllabus"] = True
        context["course"] = self.course
        context["syllabi"] = self.course.get_syllabus()
        return context

    def get(self, request, *args, **kwargs):
        syllabus_list = self.course.get_syllabus()
        formset = SyllabusFormSet(queryset=syllabus_list)
        return render(request, self.template_name, self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset = SyllabusFormSet(request.POST)

        for form in formset:
            form.data = form.data.copy() 
            form.data[form.add_prefix('course')] = str(self.course.id) 

        print("Formset Data:", request.POST)
        for form in formset:
            print("Form data for form:", form.data) 

        if formset.is_valid():
            for syllabus_form in formset:
                if syllabus_form.cleaned_data and not syllabus_form.cleaned_data.get("DELETE", False):
                    syllabus_item = syllabus_form.save(commit=False)
                    syllabus_item.course = self.course  
                    syllabus_item.save()
            return redirect("masters:syllabus_list")
        else:
            print("Formset errors:", formset.errors)
            return self.form_invalid(formset)

    def form_invalid(self, formset):
        context = self.get_context_data(formset=formset)
        context['formset_errors'] = formset.errors  
        return render(self.request, self.template_name, context)


class SyllabusDeleteView(mixins.HybridDeleteView):
    model = Syllabus
    permissions = ("admin_staff", "branch_staff", "teacher",)


class ComplaintListView(mixins.HybridListView):
    model = ComplaintRegistration
    table_class = tables.ComplaintTable
    filterset_fields = {'branch': ['exact'],}  
    permissions = ("admin_staff", "branch_staff", "teacher", "is_superuser", "student",)
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        user = self.request.user

        if user.usertype == "student":
            queryset = queryset.filter(branch=user.branch)
        elif user.usertype == "teacher":
            queryset = queryset.exclude(complaint_type="academic")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Complaint"
        context['is_masters'] = True
        context["is_complaint"] = True
        user_type = self.request.user.usertype
        context["can_add"] = user_type not in ("teacher", "admin_staff", "branch_staff")
        context["new_link"] = reverse_lazy("masters:complaint_create")
        return context
    

class ComplaintDetailView(mixins.HybridDetailView):
    model = ComplaintRegistration
    permissions = ("admin_staff", "branch_staff", "teacher", "student")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Complaint"
        return context
    

class ComplaintCreateView(mixins.HybridCreateView):
    model = ComplaintRegistration
    permissions = ("admin_staff", "branch_staff", "teacher", "student")
    exclude = ("status", "is_active", "branch")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Complaint"
        return context
    
    def get_success_url(self):
        return reverse_lazy("masters:complaint_detail", kwargs={"pk": self.object.pk})

    

class ComplaintUpdateView(mixins.HybridUpdateView):
    model = ComplaintRegistration
    permissions = ("admin_staff", "branch_staff", "teacher",)
    form_class = forms.ComplaintForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Complaint"
        return context
    

class ComplaintDeleteView(mixins.HybridDeleteView):
    model = ComplaintRegistration
    permissions = ("admin_staff", "branch_staff", "teacher",)