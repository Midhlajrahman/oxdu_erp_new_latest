from core.base import BaseAdmin

from .models import Batch, Course, PdfBook
from django.contrib import admin


@admin.register(Batch)
class BatchAdmin(BaseAdmin):
    pass


@admin.register(Course)
class CourseAdmin(BaseAdmin):
    pass


@admin.register(PdfBook)
class PdfBookAdmin(BaseAdmin):
    pass