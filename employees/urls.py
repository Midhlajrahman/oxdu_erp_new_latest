from . import views
from django.urls import path


app_name = "employees"

urlpatterns = [
    path("department/", views.DepartmentListView.as_view(), name="department_list"),
    path("department/<str:pk>/", views.DepartmentDetailView.as_view(), name="department_detail"),
    path("new/department/", views.DepartmentCreateView.as_view(), name="department_create"),
    path("department/<str:pk>/update/", views.DepartmentUpdateView.as_view(), name="department_update"),
    path("department/<str:pk>/delete/", views.DepartmentDeleteView.as_view(), name="department_delete"),
    #
    path("designation/", views.DesignationListView.as_view(), name="designation_list"),
    path("designation/<str:pk>/", views.DesignationDetailView.as_view(), name="designation_detail"),
    path("new/designation/", views.DesignationCreateView.as_view(), name="designation_create"),
    path("designation/<str:pk>/update/", views.DesignationUpdateView.as_view(), name="designation_update"),
    path("designation/<str:pk>/delete/", views.DesignationDeleteView.as_view(), name="designation_delete"),
    #
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("employees/", views.EmployeeListView.as_view(), name="employee_list"),
    path("employees/add/", views.EmployeeCreateView.as_view(), name="employee_create"),
    path("view/<pk>/", views.EmployeeDetailView.as_view(), name="employee_detail"),
    path("employees/change/<pk>/", views.EmployeeUpdateView.as_view(), name="employee_update"),
    path("employees/delete/<pk>/", views.EmployeeDeleteView.as_view(), name="employee_delete"),
]
