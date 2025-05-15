from . import views
from django.urls import path


app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),

    path('settings/', views.Settings.as_view(), name='setting_list'),
    path("academic-year/<str:pk>/", views.SettingsDetailView.as_view(), name="setting_detail"),
    path('settings-create/', views.SettingsCreate.as_view(), name='setting_create'),
    path("academic-year/<str:pk>/update/", views.SettingsUpdateView.as_view(), name="setting_update"),
    path("academic-year/<str:pk>/delete/", views.SettingsDeleteView.as_view(), name="setting_delete"),

    #  academic year
    path("academic-year/", views.AcademicYearListView.as_view(), name="academicyear_list"),
    path("academic-year/<str:pk>/", views.AcademicYearDetailView.as_view(), name="academicyear_detail"),
    path("new/academic-year/", views.AcademicYearCreateView.as_view(), name="academicyear_create"),
    path("academic-year/<str:pk>/update/", views.AcademicYearUpdateView.as_view(), name="academicyear_update"),
    path("academic-year/<str:pk>/delete/", views.AcademicYearDeleteView.as_view(), name="academicyear_delete"),

    #ID Card
    path("id-card/<str:pk>/", views.IDCardView.as_view(), name="id_card"),
    path("id-card/", views.MyIDCardView.as_view(), name="my_id_card"),
    
]
