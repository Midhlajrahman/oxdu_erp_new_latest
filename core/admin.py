from .base import BaseAdmin
from .models import AcademicYear
from .models import Link
from .models import Setting
from django.contrib import admin


@admin.register(Setting)
class SettingAdmin(BaseAdmin):
    list_display = ("branch", "document_settings")
    search_fields = ("branch__name",)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("__str__",)


@admin.register(Link)
class LinkAdmin(BaseAdmin):
    readonly_fields = ()
    search_fields = ("view", "name", "value", "module", "description")
    paginate_by = 300
    list_display = ("view", "module", "name", "gen_link", "employee_access", "admin_staff_access")
    list_filter = ("module", "view_type", "is_hidden", "is_dashboard_link", "created", "employee_access", "admin_staff_access")
    list_editable = ("employee_access", "admin_staff_access")
