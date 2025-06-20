from core.base import BaseAdmin

from .models import Batch, Course, PdfBook, Syllabus, BatchSyllabusStatus
from django.contrib import admin


@admin.register(Batch)
class BatchAdmin(BaseAdmin):
    list_display = ("__str__", "branch",)


@admin.register(Course)
class CourseAdmin(BaseAdmin):
    pass


@admin.register(PdfBook)
class PdfBookAdmin(BaseAdmin):
    pass


@admin.register(Syllabus)
class SyllabusAdmin(BaseAdmin):
    list_display = ("course", "created")
    search_fields = ("course__name",)
    list_filter = ("course",)


@admin.register(BatchSyllabusStatus)
class BatchSyllabusStatusAdmin(BaseAdmin):
    list_display = ("batch", "syllabus", "user", "status")