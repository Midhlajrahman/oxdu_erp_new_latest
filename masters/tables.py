from core.base import BaseTable
from django_tables2 import columns
from admission .models import Admission
from employees .models import Employee
from .models import Batch, Course, PDFBookResource, PdfBook, ComplaintRegistration, ChatSession, Update, PlacementRequest


class BatchTable(BaseTable):
    created = None
    class Meta(BaseTable.Meta):
        model = Batch
        fields = ("branch", "batch_name", "course", "starting_date", "ending_date", "starting_time", "ending_time", )
        
    
class CourseTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Course
        fields = ("name", )


class PDFBookResourceTable(BaseTable):
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
    class Meta(BaseTable.Meta):
        model = PDFBookResource
        fields = ("course", )
        
    
class PdfBookTable(BaseTable):
    action = columns.TemplateColumn(
        """
        <div class="btn-group">
            <a href="{{ record.pdf.url }}" class="btn btn-sm btn-light btn-outline-info">OPEN</a>
        </div>
        """,
        orderable=False,
    )
    class Meta(BaseTable.Meta):
        model = PdfBook
        fields = ("name", "pdf", "created", "action")
    

class SyllabusBatchTable(BaseTable):
    action = columns.TemplateColumn(
        """
        <div class="btn-group">
            <a class="btn btn-default mx-1 btn-sm" title='View' href="{% url 'masters:syllabus_detail' course_pk=record.course.pk batch_pk=record.pk %}"><i class="fa fa-eye"></i></a>
        </div>
        """,
        orderable=False,
    )

    class Meta(BaseTable.Meta):
        model = Batch
        fields = ("branch", "batch_name", "course", "academic_year")
        attrs = {"class": "table table-striped table-bordered"}

    
class ComplaintTable(BaseTable):
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
    class Meta(BaseTable.Meta):
        model = ComplaintRegistration
        fields = ("created", "branch", "complaint_type", "status",)
        attrs = {"class": "table table-striped table-bordered"}

    
class ChatSessionTable(BaseTable):
    action = columns.TemplateColumn(
        template_code="""
        {% if record.user and record.user.id %}
            <a href="{% url 'masters:student_chat' record.user.id %}" class="btn msg-btn btn-sm btn-primary position-relative">
                <i class="fas fa-comments fa-2x"></i>
                {% if record.unread_count > 0 %}
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                        {{ record.unread_count }}
                    </span>
                {% endif %}
            </a>
        {% else %}
            <span class="text-muted">No user assigned</span>
        {% endif %}
        """,
        orderable=False,
        verbose_name="Chat"
    )

    class Meta(BaseTable.Meta):
        model = Admission
        fields = ("admission_number", "fullname", "user", "course", 'batch')
        attrs = {"class": "table table-striped table-bordered"}

    
class EmployeeChatSessionTable(BaseTable):
    action = columns.TemplateColumn(
        template_code="""
        {% if record.user and record.user.id %}
            <a href="{% url 'masters:student_chat' record.user.id %}" class="btn msg-btn btn-sm btn-primary position-relative">
                <i class="fas fa-comments fa-2x"></i>
                {% if record.unread_count %}
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                        {{ record.unread_count }}
                    </span>
                {% endif %}
            </a>
        {% else %}
            <span class="text-muted">No user assigned</span>
        {% endif %}
        """,
        orderable=False,
        verbose_name="Chat"
    )
    user__usertype = columns.Column(
        accessor="user.usertype",
        verbose_name="User Type",
    )
    fullname = columns.Column(
        accessor="fullname",
        verbose_name="Full Name",
    )
    created = None

    class Meta(BaseTable.Meta):
        model = Employee
        fields = ("employee_id", "fullname", "personal_email", "user__usertype")
        attrs = {"class": "table table-striped table-bordered"}

    
class UpdateTable(BaseTable):
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
    class Meta(BaseTable.Meta):
        model = Update
        fields = ("title", )
        attrs = {"class": "table table-striped table-bordered"}

    
    
class PlacementRequestTable(BaseTable):
    student__admission_number = columns.Column(
        accessor="student.admission_number",
        verbose_name="Admission Number",
    )
    student__course = columns.Column(
        accessor="student.course",
        verbose_name="Course",
    )
    student__batch = columns.Column(
        accessor="student.batch",
        verbose_name="Batch",
    )
    student__age = columns.Column(
        accessor="student.age",
        verbose_name="Age", 
        attrs={"td": {"style": "font-weight: bold;"}}
    )
    
    class Meta(BaseTable.Meta):
        model = PlacementRequest
        fields = ("student__admission_number", "student", "student__age", "student__course", "student__batch", "status",)
        attrs = {"class": "table table-striped table-bordered"}