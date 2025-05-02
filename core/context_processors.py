from core.models import AcademicYear
from branches.models import Branch
from admission.models import Admission

from django.conf import settings


def main_context(request):
    user = request.user if request.user.is_authenticated else None
    # name = user.username if user else None
    name = user.email if user else None

    # Fetch academic year and branch if session keys exist
    academic_year_id = request.session.get('academic_year')
    branch_id = request.session.get('branch')

    loged_academic_year = AcademicYear.objects.filter(id=academic_year_id).first() if academic_year_id else None
    loged_branch = Branch.objects.filter(id=branch_id).first() if branch_id else None
    
    admission = None
    if request.user.is_authenticated and request.user.usertype == 'student':
        admission = Admission.objects.filter(user=request.user).select_related('course').first()

    return {
        "current_employee": user,
        "default_user_avatar": f"https://ui-avatars.com/api/?name={name or ''}&background=fdc010&color=fff&size=128",
        "app_settings": settings.APP_SETTINGS,
        "loged_academic_year": loged_academic_year,
        "loged_branch": loged_branch,
        'admission': admission
    }
