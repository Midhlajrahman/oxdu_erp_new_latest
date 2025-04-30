from core.base import BaseTable
from django_tables2 import columns
from .models import Batch, Course, PDFBookResource, PdfBook, ComplaintRegistration, Syllabus


class BatchTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Batch
        fields = ("branch", "batch_name", "academic_year",)
        
    
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
            <a class="btn btn-default mx-1 btn-sm" title='View' href="{{record.get_syllabus_detail_url}}"><i class="fa fa-eye"></i></a>
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