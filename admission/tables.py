from core.base import BaseTable
import django_tables2 as tables
from django_tables2 import columns
from django.utils.html import format_html


from .models import Admission, AttendanceRegister, FeeReceipt

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

    class Meta:
        model = Admission
        fields = ("admission_number","admission_date","fullname", "course", "contact_number", "is_active", "action")
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
    
    def render_get_total_fee_amount(self, value):
        return format_html('<span style="font-weight: bold; color: green;">{}</span>', value)

    def render_get_balance_amount(self, value):
        return format_html('<span style="font-weight: bold; color: red;">{}</span>', value)
    
    class Meta:
        model = Admission
        fields = ("fullname", "admission_number", "course", "course__fees", "get_total_fee_amount", "get_balance_amount", "action")
        attrs = {"class": "table key-buttons border-bottom table-hover table-bordered"}