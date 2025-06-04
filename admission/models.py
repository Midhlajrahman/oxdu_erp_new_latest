from django.core.validators import RegexValidator
import os
import uuid
from django.db.models import Sum
    
from core.base import BaseModel
from django.db import models

from core.choices import BLOOD_CHOICES, BOOL_CHOICES, CHOICES, FEE_STRUCTURE_TYPE, FEE_TYPE, PAYMENT_METHOD_CHOICES
from core.choices import GENDER_CHOICES
from core.choices import RELIGION_CHOICES
from core.choices import PAYMENT_PERIOD_CHOICES
from core.choices import ATTENDANCE_STATUS
from core.choices import MONTH_CHOICES, ENQUIRY_TYPE_CHOICES, ENQUIRY_STATUS

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from datetime import datetime

from admission.utils import send_sms

phone_validator = RegexValidator(
    regex=r'^91\d{10}$',
    message='Enter number in international format like 91987654321 (no + or spaces).'
)

def generate_admission_no(course):
    first_letter = course.name[0].upper() if course and course.name else 'X'
    prefix = f"OX{first_letter}"
    last_admission = Admission.objects.filter(admission_number__startswith=prefix).order_by('-admission_number').first()

    if last_admission and last_admission.admission_number:
        try:
            last_number = int(last_admission.admission_number.replace(prefix, ""))
            next_number = last_number + 1
        except ValueError:
            next_number = 1
    else:
        next_number = 1

    return f"{prefix}{str(next_number).zfill(3)}"


def generate_receipt_no():
    max_receipt_no = FeeReceipt.objects.aggregate(models.Max('receipt_no'))['receipt_no__max']
    
    if max_receipt_no is None:
        receipt_no = 1
    else:
        try:
            receipt_no = int(max_receipt_no.replace("OXD00", "")) + 1  
        except ValueError:
            raise ValueError("Invalid receipt number format in database")

    return f"OXD00{receipt_no}"  


def active_objects():
    return {'is_active': True}


class Admission(BaseModel):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name="student",null=True, )
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE) 
    first_name = models.CharField(max_length=200,null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    joining_date = models.DateField(null=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    blood_group = models.CharField(max_length=20,choices=BLOOD_CHOICES, blank=True, null=True)
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    
    home_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=180, blank=True, null=True)
    district = models.CharField(max_length=180, blank=True, null=True)
    state = models.CharField(max_length=180, blank=True, null=True)
    pin_code = models.CharField(max_length=180, blank=True, null=True)
    
    personal_email = models.EmailField(null=True, unique=True)
    contact_number = models.CharField(max_length=30,null=True,)
    whatsapp_number = models.CharField(max_length=30,null=True,)
    
    admission_number = models.CharField(max_length=10, null=True, blank=True)
    admission_date = models.DateField(default=timezone.now)
    photo = models.FileField(upload_to="admission/documents/", null=True, blank=True)
    
    course = models.ForeignKey('masters.Course', on_delete=models.CASCADE, limit_choices_to={"is_active": True}, null=True,)
    batch = models.ForeignKey('masters.Batch',on_delete= models.CASCADE,limit_choices_to={"is_active": True}, null=True)
    other_details = models.TextField(blank=True, null=True)
    document = models.FileField(upload_to="admission/documents/", null=True, blank=True)
    signature = models.FileField(upload_to="admission/signature/", null=True, blank=True)
    
    # Parent Info
    parent_first_name = models.CharField(max_length=200,null=True,)
    parent_last_name = models.CharField(max_length=200, blank=True, null=True)
    parent_contact_number = models.CharField(max_length=12, null=True, validators=[phone_validator], help_text="Enter Contact number with country code, e.g. 91987654321")
    parent_whatsapp_number = models.CharField(max_length=12, null=True, validators=[phone_validator],help_text="Enter WhatsApp number with country code, e.g. 91987654321")
    parent_mail_id = models.EmailField(verbose_name="Mail Id", null=True, blank=True)
    
    # finance
    fee_type = models.CharField(max_length=30, choices=FEE_TYPE, blank=True, null=True)
    is_discount = models.CharField(max_length=30, choices=CHOICES, blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    
    def fullname(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def parentfullname(self):
        if self.parent_last_name:
            return f"{self.parent_first_name} {self.parent_last_name}"
        return self.parent_first_name
    
    def age(self):
        if self.date_of_birth:
            today = datetime.now().date()
            return today.year - self.date_of_birth.year

    def __str__(self):
        return f"{self.fullname()} - {self.admission_number}"

    @staticmethod
    def get_list_url():
        return reverse_lazy("admission:admission_list")

    def get_absolute_url(self):
        return reverse_lazy("admission:admission_detail", kwargs={"pk": self.pk})
    
    def get_update_url(self):
        return reverse_lazy("admission:admission_update", kwargs={"pk": self.pk})
    
    def get_admission_url(self):
        return reverse_lazy("admission:admission_create", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("admission:admission_delete", kwargs={"pk": self.pk})

    def get_syllabus_detail_url(self):
        return reverse_lazy("masters:syllabus_detail", kwargs={"course_pk": self.course.pk, "batch_pk": self.batch.pk})

    def get_id_card_absolute_url(self):
        return reverse_lazy("core:id_card", kwargs={"pk": self.pk})
    
    @staticmethod
    def get_fee_overview_list_url():
        return reverse_lazy("admission:student_fee_overview_list")
    
    def get_fee_overview_absolute_url(self):
        return reverse_lazy("admission:student_fee_overview_detail", kwargs={"pk": self.pk})
    
    def save(self, *args, **kwargs):
        if not self.admission_number and self.course:
            self.admission_number = generate_admission_no(self.course)

        if not self.pk and self.photo:
            self.photo.name = f"{uuid.uuid4()}{os.path.splitext(self.photo.name)[1]}"

        super().save(*args, **kwargs)


    def get_total_fee_amount(self):
        return FeeReceipt.objects.filter(student=self).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    
    def get_balance_amount(self):
        total_paid = FeeReceipt.objects.filter(student=self).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        return self.course.fees - total_paid
    
    def get_fee(self):
        return FeeStructure.objects.filter(course=self.course)
    

class AttendanceRegister(BaseModel):
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE, limit_choices_to=active_objects, null=True)
    batch = models.ForeignKey("masters.Batch", on_delete=models.CASCADE, limit_choices_to=active_objects, null=True)
    date = models.DateField(null=True,)
    course = models.ForeignKey('masters.Course', on_delete=models.CASCADE, limit_choices_to={"is_active": True}, null=True,)
    
    def __str__(self):
        return f"{self.batch} - {self.date}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Batch Attendance Register"
        verbose_name_plural = "Batch Attendance Registers"
        
    def get_attendence(self):
        return Attendance.objects.filter(register=self)
    
    def get_total_attendence(self):
        return self.get_attendence().count()
    
    def get_total_present(self):
        return self.get_attendence().filter(status='Present').count()
    
    def get_total_absent(self):
        return self.get_attendence().filter(status='Absent').count()

    def get_absolute_url(self):
        return reverse_lazy("admission:attendance_register_detail", kwargs={"pk": self.pk})

    @staticmethod
    def get_list_url():
        return reverse_lazy("admission:attendance_register_list")

    def get_update_url(self):
        return reverse_lazy("admission:attendance_register_update", kwargs={"pk": self.pk})
    
    def get_delete_url(self):
        return reverse_lazy("admission:attendance_register_delete", kwargs={"pk": self.pk})
    
    
class Attendance(BaseModel):
    register = models.ForeignKey(AttendanceRegister, on_delete=models.CASCADE)
    student = models.ForeignKey(Admission, on_delete=models.CASCADE,limit_choices_to={'is_active': True,})
    login_time = models.TimeField(null=True,)
    logout_time = models.TimeField(null=True,)
    status = models.CharField(max_length=30,choices=ATTENDANCE_STATUS)

    def __str__(self):
        return f"{self.student.fullname()} - {self.register.date} - {self.status}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.status == 'Absent':
            phone_number = self.student.parent_whatsapp_number
            if phone_number:
                combined_message = (
                    f"*Oxdu Tech School - Attendance Notification / ഹാജര്‍ അറിയിപ്പ്*\n\n"
                    
                    f"*English:*\n"
                    f"Dear Parent,\n\n"
                    f"This is to inform you that your child *{self.student.fullname()}* "
                    f"was marked absent on *{self.register.date.strftime('%B %d, %Y')}*.\n"
                    f"If there is a valid reason for the absence, kindly inform the office.\n\n"
                    
                    f"*Malayalam:*\n"
                    f"പ്രിയപ്പെട്ട രക്ഷിതാവേ,\n\n"
                    f"താങ്കളുടെ മകന്‍/മകളായ *{self.student.fullname()}* "
                    f"*{self.register.date.strftime('%Y-%m-%d')}* തീയതിയില്‍ ഹാജരായിരുന്നില്ല.\n"
                    f"ആയതിനാൽ യഥാർത്ഥ കാരണം ദയവായി അറിയിക്കുക.\n\n"
                    
                    f"Regards,\n"
                    f"*Oxdu Tech School*"
                )
                send_sms(phone_number, combined_message)

    def get_absolute_url(self):
        return reverse_lazy("admission:attendance_register_detail", kwargs={"pk": self.pk})

    @staticmethod
    def get_list_url():
        return reverse_lazy("admission:attendance_register_list")

    def get_update_url(self):
        return reverse_lazy("admission:attendance_register_update", kwargs={"pk": self.pk})
    
    def get_delete_url(self):
        return reverse_lazy("admission:attendance_register_delete", kwargs={"pk": self.pk})
    
    class Meta:
        ordering = ['id']
        
    
class FeeStructure(BaseModel):
    course = models.ManyToManyField('masters.Course',blank=True,)
    name = models.CharField(max_length=128,choices=FEE_STRUCTURE_TYPE)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Student Fee Structure"
        verbose_name_plural = "Student Fee Structures"
        

class StudentFee(BaseModel):
    student = models.ForeignKey(Admission, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.fullname()} - {self.fee_structure.name}"
    
    
class FeeReceipt(BaseModel):
    student = models.ForeignKey(Admission, on_delete=models.PROTECT)
    receipt_no = models.CharField(max_length=10,default=generate_receipt_no, null=True)
    date = models.DateTimeField(null=True)
    note = models.CharField(max_length=128,blank=True,null=True)
    payment_type = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, )
    
    def __str__(self):
        return f"Receipt No: {self.receipt_no} - Student: {self.student} - Amount: {self.amount}"
    
    def get_total_amount(self):
        return FeeReceipt.objects.filter(student=self.student).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    
    def get_balance_amount(self):
        total_paid = FeeReceipt.objects.filter(student=self.student).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        return self.student.course.fees - total_paid
    
    def get_receipt_balance(self):
        total_course_fees = self.student.course.fees 
        
        previous_payments = FeeReceipt.objects.filter(
            student=self.student, 
            id__lt=self.id  
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        remaining_balance = total_course_fees - previous_payments
        
        receipt_balance = remaining_balance - self.amount  

        return max(receipt_balance, 0)
    
    def get_due_amount(self):
        total_course_fees = self.student.course.fees 
        
        previous_payments = FeeReceipt.objects.filter(
            student=self.student, 
            id__lt=self.id  
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        remaining_balance = total_course_fees - previous_payments
        
        due_amount = remaining_balance - self.amount  

        return max(due_amount, 0)

    class Meta:
        ordering = ("-date",)
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("admission:fee_receipt_list")

    def get_absolute_url(self):
        return reverse_lazy("admission:fee_receipt_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse_lazy("admission:fee_receipt_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("admission:fee_receipt_delete", kwargs={"pk": self.pk})


class AdmissionEnquiry(BaseModel):
    enquiry_type = models.CharField(max_length=80, choices=ENQUIRY_TYPE_CHOICES, default="public_lead")
    tele_caller = models.ForeignKey("employees.Employee", on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=200, null=True)
    contact_number = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=180, blank=True, null=True)
    branch = models.ForeignKey("branches.Branch", on_delete=models.CASCADE, limit_choices_to=active_objects, null=True, blank=True)
    course = models.ForeignKey('masters.Course', on_delete=models.CASCADE, limit_choices_to={"is_active": True}, null=True, blank=True)
    date = models.DateField(null=True)
    status = models.CharField(max_length=30, choices=ENQUIRY_STATUS, default="new_enquiry")
    next_enquiry_date = models.DateField(null=True, blank=True) 
    remark = models.TextField(blank=True, null=True)

    # Student Info
   
    district = models.CharField(max_length=180, blank=True, null=True)
    state = models.CharField(max_length=180, blank=True, null=True)

    def str(self):
        return f"{self.full_name}"

    class Meta:
        ordering = ['-id']  
        verbose_name = 'Admission Enquiry'
        verbose_name_plural = 'Admission Enquiries'
    
    @staticmethod
    def get_list_url():
        return reverse_lazy("admission:admission_enquiry")

    def get_absolute_url(self):
        return reverse_lazy("admission:admission_enquiry_detail", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse_lazy("admission:admission_enquiry_update", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy("admission:admission_enquiry_delete", kwargs={"pk": self.pk})
    
    