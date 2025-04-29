from . import views
from django.urls import path


app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path('general-settings/', views.GeneralSettings.as_view(), name='general_settings'),
    path('group-settings/', views.GroupSettings.as_view(), name='group_settings'),
    path('account-settings/', views.AccountSettings.as_view(), name='account_settings'),
    
    #  academic year
    path("academic-year/", views.AcademicYearListView.as_view(), name="academicyear_list"),
    path("academic-year/<str:pk>/", views.AcademicYearDetailView.as_view(), name="academicyear_detail"),
    path("new/academic-year/", views.AcademicYearCreateView.as_view(), name="academicyear_create"),
    path("academic-year/<str:pk>/update/", views.AcademicYearUpdateView.as_view(), name="academicyear_update"),
    path("academic-year/<str:pk>/delete/", views.AcademicYearDeleteView.as_view(), name="academicyear_delete"),
    
]
