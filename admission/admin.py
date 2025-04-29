from django.contrib import admin
from .models import FeeReceipt, StudentFee,AttendanceRegister, FeeStructure, Attendance, Admission

# Register your models here.

@admin.register(AttendanceRegister)
class AttendanceRegisterAdmin(admin.ModelAdmin):
    pass


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    pass


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    pass

@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    pass

@admin.register(FeeReceipt)
class FeeReceiptAdmin(admin.ModelAdmin):
    pass

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ("fullname", "branch", "course", "is_active",)
    list_filter = ("branch", "course", "is_active")