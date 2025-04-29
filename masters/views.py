import datetime
import json
from django.shortcuts import get_object_or_404
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
from masters .forms import PdfBookFormSet, SyllabusItemFormSet, SyllabusForm
from .models import Batch, ComplaintRegistration, Course, PDFBookResource, PdfBook, Syllabus, SyllabusItem

@csrf_exempt
def status_update(request, pk):
    try:
        data = json.loads(request.body) 

        syllabus = get_object_or_404(Syllabus, pk=pk)

        if data.get('status') in dict(SyllabusItem.STATUS_CHOICES):
            syllabus_item.status = data['status']  
            syllabus_item.save()  

            return JsonResponse({"status": "success"}, status=200)
        else:
            error_message = "Invalid status"
            print(error_message)  
            return JsonResponse({"status": "error", "message": error_message}, status=400)

    except json.JSONDecodeError as e:
        error_message = f"Invalid JSON format: {str(e)}"
        print(error_message)  
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        print(error_message)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


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

        context["is_transportation"] = True
        context["is_rout"] = True
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
        context["title"] = "Create Rout"
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
    model = Syllabus
    table_class = tables.SyllabusTable 
    filterset_fields = {'batch': ['exact'], 'course': ['exact']}  
    permissions = ("")
    template_name = 'masters/syllabus/list.html'
    branch_filter = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["batches"] = Batch.objects.filter(is_active=True)
        context["title"] = "Syllabus"
        context['is_masters'] = True
        context["is_syllabus"] = True  
        return context
    

class SyllabusDetailView(mixins.HybridDetailView):
    model = Syllabus
    permissions = ()
    template_name = "masters/syllabus/object_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Syllabus"
        return context


class SyllabusCreateView(mixins.HybridCreateView):
    model = Syllabus
    permissions = ("")
    exclude = ("is_active",)
    template_name = "masters/syllabus/object_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Syllabus"
        context["is_masters"] = True
        context["is_syllabus"] = True

        if self.request.POST:
            context['formset'] = SyllabusItemFormSet(self.request.POST)
        else:
            context['formset'] = SyllabusItemFormSet(queryset=SyllabusItem.objects.none())

        context['form'] = SyllabusForm()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            syllabus = form.save(commit=False)
            syllabus.save()

            for syllabus_item_form in formset:
                syllabus_item = syllabus_item_form.save(commit=False)
                syllabus_item.syllabus = syllabus
                syllabus_item.save()

            formset.save() 

            return super().form_valid(form)
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)

            for form_in_set in formset:
                print("Formset form errors:", form_in_set.errors)

            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        print("Form errors (invalid):", form.errors)
        return self.render_to_response(context)


class SyllabusUpdateView(mixins.HybridUpdateView):
    model = Syllabus
    permissions = ("")
    exclude = ("is_active",)
    template_name = "masters/syllabus/object_form.html"


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