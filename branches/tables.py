from core.base import BaseTable

from .models import Branch


class BranchTable(BaseTable):
    class Meta(BaseTable.Meta):
        model = Branch
        fields = ("name", "city", "contact_number", "email")
