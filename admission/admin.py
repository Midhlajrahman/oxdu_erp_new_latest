from django.contrib import admin
from core.base import BaseAdmin
from .models import FeeReceipt, StudentFee,AttendanceRegister, FeeStructure, Attendance, Admission, AdmissionEnquiry

# Register your models here.

@admin.register(AttendanceRegister)
class AttendanceRegisterAdmin(BaseAdmin):
    pass


@admin.register(Attendance)
class AttendanceAdmin(BaseAdmin):
    pass


@admin.register(FeeStructure)
class FeeStructureAdmin(BaseAdmin):
    pass

@admin.register(StudentFee)
class StudentFeeAdmin(BaseAdmin):
    pass

@admin.register(FeeReceipt)
class FeeReceiptAdmin(BaseAdmin):
    pass

@admin.register(Admission)
class AdmissionAdmin(BaseAdmin):
    list_display = ("fullname", "branch", "course", "is_active",)
    list_filter = ("branch", "course", "is_active")


@admin.register(AdmissionEnquiry)
class AdmissionEnquiryAdmin(BaseAdmin):
    list_display = ("full_name", "branch", "course", 'enquiry_type', 'tele_caller', "is_active",)
    list_filter = ("branch", "course", "is_active")
