import datetime
import json
from django.db.models import Count, Q, OuterRef, Subquery, IntegerField, Exists
from django.contrib.auth import get_user_model
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
from .forms import PdfBookFormSet, SyllabusForm,SyllabusFormSet, ChatMessageForm
from .models import Batch, ComplaintRegistration, Course, PDFBookResource, PdfBook, Syllabus, BatchSyllabusStatus, ChatSession, Update, PlacementRequest

User = get_user_model()

@csrf_exempt 
def clear_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    current_user = request.user

    ChatSession.objects.filter(
        Q(sender=current_user, recipient=other_user) |
        Q(sender=other_user, recipient=current_user)
    ).delete()

    return JsonResponse({'status': 'success'})


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
    filterset_fields = {'course': ['exact'], "starting_date": ['exact'], "ending_date": ['exact'], "starting_time": ['exact'], "ending_time": ['exact'] }
    permissions = ("branch_staff", "teacher", "admin_staff" "is_superuser",)
    
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
    permissions = ("branch_staff", "teacher", "admin_staff" "is_superuser")
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
    permissions = ("superadmin",'branch_staff', "admin_staff", 'teacher', "student")
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
    permissions = ("superadmin", "branch_staff", "admin_staff",  "teacher", "student")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.get_object()

        pdfbook_entries = PdfBook.objects.filter(resource=resource, is_active=True)

        context["customer_table"] = tables.PDFBookResourceTable(pdfbook_entries)
        context["pdfbook_entries"] = pdfbook_entries 
        return context


class PDFBookResourceCreateView(mixins.HybridCreateView):
    model = PDFBookResource
    permissions = ("superadmin", "branch_staff", "admin_staff",  "teacher")
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
    permissions = ("superadmin", "branch_staff", "admin_staff",  "teacher")
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
    permissions = ("superadmin",'branch_staff', "admin_staff", 'driver')
    

class PDFBookListView(mixins.HybridListView):
    model = PdfBook
    table_class = tables.PdfBookTable
    filterset_fields = ('name',)
    permissions = ("superadmin",'branch_staff', "admin_staff", 'teacher', "student")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["courses"] = Course.objects.filter(is_active=True)
        context["title"] = "Syllabus"
        context["is_syllabus"] = True
        context["can_add"] = user.usertype not in ["student", "teacher", "mentor"]
        context["new_link"] = reverse_lazy("masters:pdfbook_resource_create")
        return context
    

class SyllabusDetailView(TemplateView):
    template_name = "masters/syllabus/object_view.html"
    permissions = ()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_pk = self.kwargs.get("course_pk")
        batch_pk = self.kwargs.get("batch_pk")

        course = get_object_or_404(Course, pk=course_pk)
        batch = get_object_or_404(Batch, pk=batch_pk)

        user = self.request.user
        branch = self.request.session.get('branch')

        syllabus_qs = Syllabus.objects.filter(course=course, is_active=True)
        syllabus_ids = syllabus_qs.values_list('id', flat=True)

        if user.usertype not in ["student", "teacher"]:
            teacher_users = User.objects.filter(employee__course=course)
            completed_statuses = BatchSyllabusStatus.objects.filter(
                syllabus_id__in=syllabus_ids,
                user__in=teacher_users
            )
            completed_status_ids = completed_statuses.values_list('syllabus_id', flat=True)
            pending_statuses = syllabus_qs.exclude(id__in=completed_status_ids)

            students = Admission.objects.filter(
                branch=branch,
                batch=batch,
                course=course,
                is_active=True
            )

            student_data = []
            for student in students:
                statuses = []
                for syllabus in syllabus_qs:
                    viewed = BatchSyllabusStatus.objects.filter(
                        syllabus=syllabus,
                        user=student.user
                    ).exists()
                    statuses.append({
                        "title": syllabus.title,
                        "week": syllabus.week,
                        "viewed": viewed
                    })
                student_data.append({
                    "name": student.fullname(),
                    "admission_number": student.admission_number,
                    "statuses": statuses
                })

            context["students"] = student_data
            context["batch"] = batch

        else:
            completed_statuses = BatchSyllabusStatus.objects.filter(
                syllabus_id__in=syllabus_ids,
                user=user
            )
            completed_status_ids = completed_statuses.values_list('syllabus_id', flat=True)
            pending_statuses = syllabus_qs.exclude(id__in=completed_status_ids)

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


class ChatListView(mixins.HybridListView):
    template_name = "masters/chat/list.html"
    model = Admission
    table_class = tables.ChatSessionTable
    filterset_fields = {'batch': ['exact'], "branch": ['exact'], 'course': ['exact']}  
    permissions = ("admin_staff", "branch_staff", "teacher", "is_superuser", "student", "mentor",)

    def get_queryset(self):
        queryset = super().get_queryset()
        current_user = self.request.user

        queryset = queryset.annotate(
            unread_count=Subquery(
                ChatSession.objects.filter(
                    sender=OuterRef('user'),
                    recipient=current_user,
                    read=False
                ).values('sender')
                .annotate(count=Count('id'))
                .values('count')[:1],
                output_field=IntegerField()
            )
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Chat Session"
        context["is_chat_session"] = True
        context["can_add"] =  False
        return context

    
class EmployeeChatListView(mixins.HybridListView):
    template_name = "masters/chat/list.html"
    model = Employee
    table_class = tables.EmployeeChatSessionTable
    filterset_fields = {"branch": ['exact'], 'course': ['exact']}  
    permissions = ("admin_staff", "branch_staff", "teacher", "is_superuser", "student", "mentor",)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Chat Session"
        context["is_mentor_chat_session"] = True
        context["can_add"] =  False
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        current_user = self.request.user

        queryset = queryset.filter(
            user__branch=current_user.branch,
            user__usertype__in=["teacher", "mentor"]
        ).annotate(
            unread_count=Subquery(
                ChatSession.objects.filter(
                    sender=OuterRef("user"),
                    recipient=current_user,
                    read=False
                )
                .values("sender")
                .annotate(count=Count("id"))
                .values("count")[:1],
                output_field=IntegerField()
            )
        )

        return queryset
    
    
class StudentChatView(TemplateView):
    template_name = "masters/chat/object_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        other_user = get_object_or_404(User, id=self.kwargs["user_id"])
        current_user = self.request.user

        messages = ChatSession.objects.filter(
            Q(sender=current_user, recipient=other_user) |
            Q(sender=other_user, recipient=current_user)
        ).order_by("created")

        messages.filter(sender=other_user, recipient=current_user, read=False).update(read=True)

        context["default_user_avatar"] = f"https://ui-avatars.com/api/?name={current_user.get_full_name()}&background=fdc010&color=fff&size=128"
        
        context["other_user_avatar"] = f"https://ui-avatars.com/api/?name={other_user.get_full_name()}&background=fdc010&color=fff&size=128"

        context["messages"] = messages
        context["other_user"] = other_user
        return context

    def post(self, request, *args, **kwargs):
        other_user = get_object_or_404(User, id=self.kwargs["user_id"])
        message = request.POST.get("message", "")
        attachment = request.FILES.get("attachment")

        if attachment and attachment.size > 1024 * 1024:
            messages.error(request, "File size should not exceed 1 MB.")
            return redirect("masters:student_chat", user_id=other_user.id)

        if message or attachment:
            ChatSession.objects.create(
                sender=request.user,
                recipient=other_user,
                message=message,
                attachment=attachment
            )

        return redirect("masters:student_chat", user_id=other_user.id)


class UpdateListView(mixins.HybridListView):
    template_name = "masters/update/list.html"
    model = Update
    table_class = tables.UpdateTable
    filterset_fields = {'created': ['exact'],}  
    permissions = ("admin_staff", "branch_staff", "teacher", "is_superuser", "student", "mentor", "tele_caller", "sales_head")
    branch_filter = False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Updates"
        context["is_update"] = True
        context["updates"] = context["object_list"]
        user_type = self.request.user.usertype
        context["can_add"] = user_type not in ("mentor", "student", "teacher", "tele_caller", "sales_head")
        context["new_link"] = reverse_lazy("masters:update_create")
        return context
    

class UpdateDetailView(mixins.HybridDetailView):
    template_name = "masters/update/detail.html"
    model = Update
    permissions = ("admin_staff", "branch_staff", "teacher", "student", "mentor", "tele_caller", "sales_head" )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Details"
        return context
    

class UpdateCreateView(mixins.HybridCreateView):
    model = Update
    permissions = ("admin_staff", "branch_staff",)
    exclude = ("status", "is_active", "branch")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update"
        return context

    def get_success_url(self):
        return reverse_lazy("masters:update_detail", kwargs={"pk": self.object.pk})


class UpdateUpdateView(mixins.HybridUpdateView):
    model = Update
    permissions = ("admin_staff", "branch_staff",)
    form_class = forms.UpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update"
        return context
    

class UpdateDeleteView(mixins.HybridDeleteView):
    model = Update
    permissions = ("admin_staff", "branch_staff",)


class PlacementRequestListView(mixins.HybridListView):
    model = PlacementRequest
    table_class = tables.PlacementRequestTable
    filterset_fields = {'student': ['exact'],}  
    permissions = ("admin_staff", "branch_staff", "teacher", "is_superuser", "student", "mentor")
    branch_filter = False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Placement Request"
        context["is_placement_request"] = True
        context["can_add"] = True
        context["new_link"] = reverse_lazy("masters:placement_request_create")
        return context
    

class PlacementRequestDetailView(mixins.HybridDetailView):
    model = PlacementRequest
    permissions = ("admin_staff", "branch_staff", "teacher", "student", "mentor")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Placement Request"
        return context
    

class PlacementRequestCreateView(mixins.HybridCreateView):
    model = PlacementRequest
    exclude = ('student', 'status', )
    permissions = ("admin_staff", "branch_staff", "mentor", "student", "teacher")

    def dispatch(self, request, *args, **kwargs):
        try:
            admission = Admission.objects.get(user=request.user)
        except Admission.DoesNotExist:
            return self.handle_no_permission()

        if PlacementRequest.objects.filter(student=admission, status__in=["Request Send", "Under Review"]).exists():
            return render(request, 'masters/placement-request/403.html', status=403)

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        try:
            admission = Admission.objects.get(user=self.request.user)
            initial["student"] = admission
        except Admission.DoesNotExist:
            pass
        return initial

    def form_valid(self, form):
        try:
            admission = Admission.objects.get(user=self.request.user)
            form.instance.student = admission
        except Admission.DoesNotExist:
            form.add_error(None, "Student record not found.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Placement Request"
        return context

    def get_success_url(self):
        return reverse_lazy("masters:update_detail", kwargs={"pk": self.object.pk})


class PlacementRequestUpdateView(mixins.HybridUpdateView):
    model = PlacementRequest
    permissions = ("admin_staff", "branch_staff", "mentor")
    form_class = forms.PlacementRequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "PlacementRequest"
        return context
    

class PlacementRequestDeleteView(mixins.HybridDeleteView):
    model = PlacementRequest
    permissions = ("admin_staff", "branch_staff", "mentor",)