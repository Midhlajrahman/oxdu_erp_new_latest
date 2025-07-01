from core.base import BaseTable, CustomBaseTable
import django_tables2 as tables
from django.utils.safestring import mark_safe 
from django_tables2 import columns
from django.utils.html import format_html

from .models import Admission, AttendanceRegister, FeeReceipt, AdmissionEnquiry

class AdmissionTable(BaseTable):
    created = None
    fullname = columns.Column(verbose_name="Student", order_by="first_name")
    course = columns.Column(verbose_name="Course")
    contact_number = columns.Column(verbose_name="Mob")
    admission_date = columns.Column(verbose_name="Admission Date")
    admission_number = columns.Column(verbose_name="Ad.No", linkify=True)
    is_active = tables.TemplateColumn(
        template_code="""
        <form method="post" action="{% url 'admission:change_status' record.pk %}">
            {% csrf_token %}
            <select name="is_active" onchange="this.form.submit()" class="form-select form-select-sm">
                <option value="True" {% if record.is_active == True %}selected{% endif %}>Active</option>
                <option value="False" {% if record.is_active == False %}selected{% endif %}>Inactive</option>
            </select>
        </form>
        """,
        orderable=False,
        verbose_name="Status"
    )

    id_card = tables.TemplateColumn(
        template_code="""
            <a href="{{ record.get_id_card_absolute_url }}" 
               class="btn btn-sm btn-outline-primary id-card-btn"
               title="Download ID Card">
                <i class="bi bi-person-badge"></i>
                <span>ID Card</span>
            </a>
        """,
        verbose_name="ID Card",
        orderable=False
    )

    class Meta:
        model = Admission
        fields = ("admission_number","admission_date","fullname", "course", "contact_number", "is_active", "action", "id_card")
        attrs = {"class": "table star-student table-hover table-bordered"}
        

class AdmissionEnquiryTable(BaseTable):
    full_name = columns.Column(verbose_name="Student")
    course = columns.Column(verbose_name="Course")
    contact_number = columns.TemplateColumn(
        verbose_name="Mob",
        template_code='<a href="tel:{{ record.contact_number }}">{{ record.contact_number }}</a>',
        orderable=False
    )
    date = columns.Column(verbose_name="Enquiry Date")
    status = columns.Column(verbose_name="Enquiry Status")
    action = tables.TemplateColumn(
        verbose_name='Action',
        template_code='''
            <a href="{{ record.get_absolute_url }}" class="btn btn-sm btn-primary">View</a>
            <a href="{{ record.get_update_url }}" class="btn btn-sm btn-warning">Edit</a>
        ''',
        orderable=False
    )
    created = None

    class Meta:
        model = AdmissionEnquiry
        fields = ("date", "full_name", "course", "contact_number", "tele_caller", "enquiry_type", "status", "action")
        attrs = {"class": "table star-student table-hover table-bordered"}

    
class PublicEnquiryListTable(CustomBaseTable):
    full_name = columns.Column(verbose_name="Full Name")
    contact_number = columns.Column(verbose_name="Contact Number")

    tele_caller_column = tables.TemplateColumn(
        template_code='''
            {% if record.tele_caller %}
                <strong>{{ record.tele_caller.user.get_full_name }}</strong>
            {% elif not table.request.user.usertype == "sales_head" %}
                <span class="text-danger">Not Assigned</span>
            {% endif %}

            {% if table.request.user.usertype == "sales_head" %}
                <select name="tele_caller"
                        class="form-select form-select-sm mt-2 bulk-assign-tele-caller"
                        data-record-id="{{ record.id }}">
                    <option value="">-- Assign Tele Caller --</option>
                    {% for caller in tele_callers %}
                        <option value="{{ caller.id }}">{{ caller.user.get_full_name }}</option>
                    {% endfor %}
                </select>
            {% endif %}
        ''',
        verbose_name='Tele Caller',
        orderable=False,
    )

    action = tables.TemplateColumn(
        template_code='''
            {% if record.tele_caller %}
                <span class="badge bg-success">Assigned</span>
            {% elif table.request.user.usertype == "tele_caller" or table.request.user.employee.is_also_tele_caller == "Yes" %}
                <a href="{% url 'admission:add_to_me' record.id %}" class="btn btn-sm btn-danger fw-bold">ADD TO ME</a>
            {% else %}
                <span class="badge bg-danger text-white">Not Assigned</span>
            {% endif %}
        ''',
        verbose_name='Action',
        orderable=False,
    )

    def render_contact_number(self, value):
        return f"**** **** {value[-4:]}" if value else ""

    class Meta:
        model = AdmissionEnquiry
        fields = ("full_name", "contact_number", "city", "enquiry_type", "tele_caller_column", "created",)
        sequence = ("selection", "...", "action")
        attrs = {"class": "table star-student table-hover table-bordered"}
    

class AttendanceRegisterTable(BaseTable):
    action = columns.TemplateColumn(
        """
        <div class="btn-group">
            <a class="btn btn-default mx-1 btn-sm" title='View' href="{{record.get_absolute_url}}"><i class="fa fa-eye"></i></a>
            <a class="btn btn-default mx-1 btn-sm" title='Edit' href="{{record.get_update_url}}"><i class="fa fa-edit"></i></a>
            <a class="btn btn-default mx-1 btn-sm" title='Delete' href="{{record.get_delete_url}}"><i class="fa fa-trash"></i></a>
        </div>
        """,
        orderable=False,
    )   
    created = None
    class Meta:
        model = AttendanceRegister
        fields = ("batch", "course", "date", "action")
        attrs = {"class": "table key-buttons border-bottom table-hover table-bordered"}
        
    
class FeeReceiptTable(BaseTable):
    action = columns.TemplateColumn(
        """
        <a href="{{ record.get_absolute_url }}" class="btn btn-sm btn-light btn-outline-info">OPEN</a>
        """,
        orderable=False,
    )
    created = None
    class Meta:
        model = FeeReceipt
        fields = ("student", "receipt_no", "date", "payment_type", "amount", "action")
        attrs = {"class": "table key-buttons border-bottom table-hover table-bordered"}
        
    
class StudentFeeOverviewTable(BaseTable):
    action = columns.TemplateColumn(
        """
        <a href="{{ record.get_fee_overview_absolute_url }}" class="btn btn-sm btn-light btn-outline-info">OPEN</a>
        """,
        orderable=False,
    )   
    created = None
    fullname = columns.Column(verbose_name="Student", order_by="Student")
    admission_number = columns.Column(verbose_name="Ad.No", linkify=True)
    course = columns.Column(verbose_name="Course")
    course__fees = columns.Column(verbose_name="Course Fees")
    get_total_fee_amount = columns.Column(verbose_name="Total Receipt", orderable=False,)
    get_balance_amount = columns.Column(verbose_name="Balance Due", orderable=False,)

    def render_course__fees(self, value):
        return format_html('<span class="fw-bold">₹{}</span>', value)
    
    def render_get_total_fee_amount(self, value):
        return format_html('<span class="fw-bold text-success">₹{}</span>', value)

    def render_get_balance_amount(self, value):
        return format_html('<span class="fw-bold text-danger">₹{}</span>', value)
    
    class Meta:
        model = Admission
        fields = ("fullname", "admission_number", "course", "course__fees", "get_total_fee_amount", "get_balance_amount", "action")
        attrs = {"class": "table key-buttons border-bottom table-hover table-bordered"}