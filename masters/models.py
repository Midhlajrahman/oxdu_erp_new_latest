from django.core.validators import FileExtensionValidator
from tinymce.models import HTMLField

from core.base import BaseModel

from django.db import models
from django.urls import reverse_lazy


class Batch(BaseModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE, null=True)
    course =models.ForeignKey("masters.Course", on_delete=models.CASCADE, null=True)
    batch_name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    starting_time = models.TimeField(blank=True, null=True)
    ending_time = models.TimeField(blank=True, null=True)
    academic_year = models.ForeignKey("core.AcademicYear", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.batch_name
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:batch_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:batch_detail", kwargs={"pk": self.pk})

    def get_syllabus_detail_url(self):
        return reverse_lazy("masters:syllabus_detail", kwargs={"pk": self.course.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:batch_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:batch_delete", kwargs={"pk": self.pk})
    
    
class Course(BaseModel):
    name = models.CharField(max_length=120)
    fees = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_syllabus(self):
        return Syllabus.objects.filter(course=self)
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:course_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:course_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:course_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:course_delete", kwargs={"pk": self.pk})
    

class PDFBookResource(BaseModel):
    course = models.ForeignKey("masters.Course", on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.course) 
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:pdf_book_resource_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:pdf_book_resource_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:pdf_book_resource_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:pdf_book_resource_delete", kwargs={"pk": self.pk})
    

class PdfBook(BaseModel):
    resource = models.ForeignKey("masters.PDFBookResource", on_delete=models.CASCADE)
    name = models.CharField(max_length=180)
    pdf = models.FileField(upload_to="pdf/")
    
    def __str__(self):
        return self.name
    
    # @staticmethod
    # def get_list_url():
    #     return reverse_lazy("masters:pdf_book_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:pdf_book_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:pdf_book_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:pdf_book_delete", kwargs={"pk": self.pk})
    

class Syllabus(BaseModel):
    course = models.ForeignKey("masters.Course", on_delete=models.CASCADE)
    week = models.CharField(max_length=120)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.course) 
    
    class Meta:
        verbose_name = 'Syllabus'
        verbose_name_plural = 'Syllabuses'

    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:syllabus_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:syllabus_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:syllabus_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:syllabus_delete", kwargs={"pk": self.pk})


class BatchSyllabusStatus(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    batch = models.ForeignKey("masters.Batch", on_delete=models.CASCADE)
    syllabus = models.ForeignKey("masters.Syllabus", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", limit_choices_to={'is_active': True}, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return str(self.batch.batch_name )
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:batch_syllabus_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:batch_syllabus_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:batch_syllabus_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:batch_syllabus_delete", kwargs={"pk": self.pk})
    

class ComplaintRegistration(BaseModel):
    COMPALINT_TYPE_CHOICES = [
        ("general", "General"),
        ("academic", "Academic"),
        ("other", "Other")
    ]
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE, null=True)
    complaint_type = models.CharField(max_length=15, choices=COMPALINT_TYPE_CHOICES, default="general")
    complaint = models.TextField()
    status = models.CharField(
        max_length=30,
        choices=[
            ("Complaint Registered", "Complaint Registered"),
            ("In Progress", "In Progress"),
            ("Resolved", "Resolved"),
            ("Closed", "Closed")
        ],
        default="Complaint Registered"
    )
    
    def __str__(self):
        return str(self.complaint_type) 
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:complaint_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:complaint_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:complaint_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:complaint_delete", kwargs={"pk": self.pk})

    
class ChatSession(BaseModel):
    sender = models.ForeignKey("accounts.User", related_name="sent_messages", on_delete=models.CASCADE, null=True)
    recipient = models.ForeignKey("accounts.User", related_name="received_messages", on_delete=models.CASCADE, null=True)
    attachment = models.FileField(
        upload_to='chat_attachments/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'])]
    )
    message = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} to {self.recipient}"
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:chat_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:chat_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:chat_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:chat_delete", kwargs={"pk": self.pk})

    
class Update(BaseModel):
    title = models.CharField(max_length=200,)
    image = models.ImageField(upload_to="updates/")
    description = HTMLField()

    def __str__(self):
        return f"{self.title}"

    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:update_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:update_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:update_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("masters:update_delete", kwargs={"pk": self.pk})

    
class PlacementRequest(BaseModel):
    student = models.OneToOneField("admission.Admission", on_delete=models.CASCADE, null=True)
    resume = models.URLField(
        verbose_name="Resume Link",
        help_text="Please provide a link to your resume."
    )
    portfolio_link = models.URLField(
        verbose_name="Portfolio Link",
        blank=True,
        help_text="Link to your portfolio or work samples"
    )
    behance_link = models.URLField(
        verbose_name="Behance Profile Link",
        blank=True,
        help_text="Link to your Behance portfolio"
    )
    experience = models.TextField(
        verbose_name="Experience",
        blank=True,
        help_text="Please provide details of your experience, if any."
    )

    status  = models.CharField(
        max_length=30,
        choices=[
            ("Request Send", "Request Send"),
            ("Under Review", "Under Review"),
            ("Completed", "Completed"),
            ("Rejected", "Rejected")
        ],
        default="Request Send"
    )

    
    def __str__(self):
        return self.student.fullname()
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("masters:placement_request_list")
    
    def get_absolute_url(self):
        return reverse_lazy("masters:placement_request_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("masters:placement_request_update", kwargs={"pk": self.pk})
    
    def get_delete_url(self):
        return reverse_lazy("masters:placement_request_delete", kwargs={"pk": self.pk})