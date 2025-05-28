from . import views
from django.urls import path


app_name = "admission"

urlpatterns = [
    path('enquiry/import/', views.ImportEnquiryView.as_view(), name='import_enquiry'),
    path("student_check_data/", views.student_check_data, name="student_check_data"),
    path('add-to-me/<int:pk>/', views.add_to_me, name='add_to_me'),
    path('assign-to/<int:pk>/', views.assign_to, name='assign_to'),
    path('bulk-assign-to/', views.assign_to, name='bulk_assign_to'),
    path('admission/<int:pk>/change-status/', views.change_status, name='change_status'),
    path('ajax/get-batches/', views.get_batches_for_course, name='get_batches_for_course'),
    
    # admission
    path("admissions/", views.AdmissionListView.as_view(), name="admission_list"),
    path("inactive-admissions/", views.InactiveAdmissionListView.as_view(), name="inactive_admission_list"),
    path("admission/<str:pk>/", views.AdmissionDetailView.as_view(), name="admission_detail"),
    path("new/admission/", views.AdmissionCreateView.as_view(), name="admission_create"),
    path("admission/<str:pk>/update/", views.AdmissionUpdateView.as_view(), name="admission_update"),
    path("admission/<str:pk>/delete/", views.AdmissionDeleteView.as_view(), name="admission_delete"),

    # enquiry
    path("public-leads/", views.PublicLeadListView.as_view(), name="public_lead_list"),
    path("my-leads/", views.MyleadListView.as_view(), name="my_lead_list"),
    path("enquiries/", views.AdmissionEnquiryView.as_view(), name="admission_enquiry"),
    path("admission-enquiry/<str:pk>/", views.AdmissionEnquiryDetailView.as_view(), name="admission_enquiry_detail"),
    path("new/admission-enquiry/<int:pk>/", views.AdmissionEnquiryCreateView.as_view(), name="admission_enquiry_create"),
    path("new/admission-enquiry/", views.AdmissionEnquiryCreateView.as_view(), name="admission_enquiry_create"),
    path("admission-enquiry/<str:pk>/update/", views.AdmissionEnquiryUpdateView.as_view(), name="admission_enquiry_update"),
    path("admission-enquiry/<str:pk>/delete/", views.AdmissionEnquiryDeleteView.as_view(), name="admission_enquiry_delete"),
    path('enquiry/delete-unassigned/', views.DeleteUnassignedLeadsView.as_view(), name='delete_unassigned_leads'),
    
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
