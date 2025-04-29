from core.base import BaseAdmin

from .models import Department, Designation, Employee
from django.contrib import admin


@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    list_display = ("name", "description", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)
    

@admin.register(Employee)
class EmployeeAdmin(BaseAdmin):
    list_display = ("first_name", "branch", "employee_id", "is_active")
    list_filter = ("is_active",)
    search_fields = ("first_name", "branch", "employee_id")
    ordering = ("first_name",)