from core.base import BaseTable

from .models import Department
from .models import Designation
from .models import Employee
from django_tables2 import columns


class EmployeeTable(BaseTable):
    employee_id = columns.Column(linkify=True)
    created = None
    fullname = columns.Column(verbose_name="Name", order_by="first_name")

    class Meta(BaseTable.Meta):
        model = Employee
        fields = ("employee_id", "branch", "fullname", "mobile", "department", "designation")


class PartnerTable(BaseTable):
    created = None
    fullname = columns.Column(order_by="first_name")

    class Meta:
        model = Employee
        fields = ("fullname", "department", "user__email")
        attrs = {"class": "table key-buttons border-bottom"}


class DepartmentTable(BaseTable):
    class Meta:
        model = Department
        fields = ("name", "department_lead")
        attrs = {"class": "table key-buttons border-bottom"}


class DesignationTable(BaseTable):
    class Meta:
        model = Designation
        fields = ("name", "description")
        attrs = {"class": "table key-buttons border-bottom"}
