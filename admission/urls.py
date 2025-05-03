from . import views
from django.urls import path


app_name = "admission"

urlpatterns = [
    path('admission/<int:pk>/change-status/', views.change_status, name='change_status'),
    path('ajax/get-batches/', views.get_batches_for_course, name='get_batches_for_course'),
    
    # admission
    path("admissions/", views.AdmissionListView.as_view(), name="admission_list"),
    path("inactive-admissions/", views.InactiveAdmissionListView.as_view(), name="inactive_admission_list"),
    path("admission/<str:pk>/", views.AdmissionDetailView.as_view(), name="admission_detail"),
    path("new/admission/", views.AdmissionCreateView.as_view(), name="admission_create"),
    path("admission/<str:pk>/update/", views.AdmissionUpdateView.as_view(), name="admission_update"),
    path("admission/<str:pk>/delete/", views.AdmissionDeleteView.as_view(), name="admission_delete"),
    
    #attendance
    path("attendance-registers/", views.AttendanceRegisterListView.as_view(), name="attendance_register_list"),
    path("attendance-register/<str:pk>/", views.AttendanceRegisterDetailView.as_view(), name="attendance_register_detail"),
    path("new/attendance-register/<int:pk>/", views.AttendanceRegisterCreateView.as_view(), name="attendance_register_create"),
    path("new/attendance-register/", views.AttendanceRegisterCreateView.as_view(), name="attendanceregister_create"),
    path("attendance-register/<str:pk>/update/", views.AttendanceRegisterUpdateView.as_view(), name="attendance_register_update"),
    path("attendance-register/<str:pk>/delete/", views.AttendanceRegisterDeleteView.as_view(), name="attendance_register_delete"),
    
    #FeeReceipt
    path("fee-receipts/", views.FeeReceiptListView.as_view(), name="fee_receipt_list"),
    path("fee-receipt/<str:pk>/", views.FeeReceiptDetailView.as_view(), name="fee_receipt_detail"),
    path("new/fee-receipt/<int:pk>/", views.FeeReceiptCreateView.as_view(), name="fee_receipt_create"),
    path("new/fee-receipt/", views.FeeReceiptCreateView.as_view(), name="feereceipt_create"),
    path("fee-receipt/<str:pk>/update/", views.FeeReceiptUpdateView.as_view(), name="fee_receipt_update"),
    path("fee-receipt/<str:pk>/delete/", views.FeeReceiptDeleteView.as_view(), name="fee_receipt_delete"),
    
    # Fee Overview
    path("students-fee-overview/", views.StudentFeeOverviewListView.as_view(), name="student_fee_overview_list"),
    path("students-fee-overview/<str:pk>/", views.StudentFeeOverviewDetailView.as_view(), name="student_fee_overview_detail"),
    
    # Student Fee Overview
    path("fee-overview/", views.FeeOverviewListView.as_view(), name="fee_overview_list"),
    
    #  registration form
    path('new/registration-form/', views.RegistrationView.as_view(), name='registration_form'),
    
    #terms-condition
    path("terms-condition/<str:pk>/", views.TermsConditionView.as_view(), name="terms_condition"),
    
    path("registration/<str:pk>/", views.RegistrationDetailView.as_view(), name="registration_detail")

]
