from . import views
from django.urls import path


app_name = "masters"

urlpatterns = [
    path('update_status/<int:pk>/', views.status_update, name='status_update'),

    # Batch
    path("batch/list/", views.BatchListView.as_view(), name="batch_list"),
    path("batch/<str:pk>/detail/", views.BatchDetailView.as_view(), name="batch_detail"),
    path("batch/create/", views.BatchCreateView.as_view(), name="batch_create"),
    path("batch/<str:pk>/update/", views.BatchUpdateView.as_view(), name="batch_update"),
    path("batch/<str:pk>/delete/", views.BatchDeleteView.as_view(), name="batch_delete"),
    
    # Course
    path("course/list/", views.CourseListView.as_view(), name="course_list"),
    path("course/<str:pk>/detail/", views.CourseDetailView.as_view(), name="course_detail"),
    path("course/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("course/<str:pk>/update/", views.CourseUpdateView.as_view(), name="course_update"),
    path("course/<str:pk>/delete/", views.CourseDeleteView.as_view(), name="course_delete"),
    
    # Pdf resource
    path("PDF-resource/list/", views.PDFBookResourceListView.as_view(), name="pdf_book_resource_list"),
    path("PDF-resource/<str:pk>/detail/", views.PDFBookResourceDetailView.as_view(), name="pdf_book_resource_detail"),
    path("new/PDF-resource/create/<str:pk>/", views.PDFBookResourceCreateView.as_view(), name="pdfbook_resource_create"),
    path("new/PDF-resource/create/", views.PDFBookResourceCreateView.as_view(), name="pdfbook_resource_create"),
    path("PDF-resource/<str:pk>/update/", views.PDFBookResourceUpdateView.as_view(), name="pdf_book_resource_update"),
    path("PDF-resource/<str:pk>/delete/", views.PDFBookResourceDeleteView.as_view(), name="pdf_book_resource_delete"),
    
    #Pdf List
    path("PDF/list/", views.PDFBookListView.as_view(), name="pdf_book_list"),
    # path("PDF/<str:pk>/detail/", views.PDFBookDetailView.as_view(), name="pdf_book_detail"),
    
    #Syllabus
    path("syllabus/list/", views.SyllabusListView.as_view(), name="syllabus_list"),
    # path("syllabus/<str:pk>/detail/", views.SyllabusDetailView.as_view(), name="syllabus_detail"),
    path('syllabus/<int:course_pk>/<int:batch_pk>/detail/', views.SyllabusDetailView.as_view(), name='syllabus_detail'),
    path('courses/<int:course_id>/syllabus/create/', views.SyllabusCreateView.as_view(), name='syllabus_create'),
    path("new/syllabus/", views.SyllabusCreateView.as_view(), name="syllabus_create"),
    path("syllabus/<str:pk>/update/", views.SyllabusUpdateView.as_view(), name="syllabus_update"),
    path('courses/<int:course_id>/syllabus/update/', views.SyllabusUpdateView.as_view(), name='syllabus_create'),
    path("syllabus/<str:pk>/delete/", views.SyllabusDeleteView.as_view(), name="syllabus_delete"),

    #Complaint
    path("complaint/list/", views.ComplaintListView.as_view(), name="complaint_list"),
    path("complaint/<str:pk>/detail/", views.ComplaintDetailView.as_view(), name="complaint_detail"),
    path("new/complaint/<str:pk>/", views.ComplaintCreateView.as_view(), name="complaint_create"),
    path("new/complaint/", views.ComplaintCreateView.as_view(), name="complaint_create"),
    path("complaint/<str:pk>/update/", views.ComplaintUpdateView.as_view(), name="complaint_update"),
    path("complaint/<str:pk>/delete/", views.ComplaintDeleteView.as_view(), name="complaint_delete"),

    #Update
    path("update/list/", views.UpdateListView.as_view(), name="update_list"),
    path("update/<str:pk>/detail/", views.UpdateDetailView.as_view(), name="update_detail"),
    path("new/update/<str:pk>/", views.UpdateCreateView.as_view(), name="update_create"),
    path("new/update/", views.UpdateCreateView.as_view(), name="update_create"),
    path("update/<str:pk>/update/", views.UpdateUpdateView.as_view(), name="update_update"),
    path("update/<str:pk>/delete/", views.UpdateDeleteView.as_view(), name="update_delete"),

    #Placement Request
    path("placement-requests/list/", views.PlacementRequestListView.as_view(), name="placement_request_list"),
    path("placement-request/<str:pk>/detail/", views.PlacementRequestDetailView.as_view(), name="placement_request_detail"),
    path("new/placement-request/<str:pk>/", views.PlacementRequestCreateView.as_view(), name="placement_request_create"),
    path("new/placement-request/", views.PlacementRequestCreateView.as_view(), name="placement_request_create"),
    path("placement-request/<str:pk>/update/", views.PlacementRequestUpdateView.as_view(), name="placement_request_update"),
    path("placement-request/<str:pk>/delete/", views.PlacementRequestDeleteView.as_view(), name="placement_request_delete"),

    #Chat
    path("chat/list/", views.ChatListView.as_view(), name="chat_list"),
    path("chat/employee/list/", views.EmployeeChatListView.as_view(), name="employee_chat_list"),
    path('chat/student/<int:user_id>/', views.StudentChatView.as_view(), name='student_chat'),
    path('chat/<int:user_id>/clear/', views.clear_chat, name='clear_chat')

]
