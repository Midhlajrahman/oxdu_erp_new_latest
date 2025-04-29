from . import views
from django.urls import path


app_name = "accounting"

urlpatterns = [
    # group
    path("groups/", views.GroupMasterListView.as_view(), name="group_master_list"),
    path("group_master/<str:pk>/", views.GroupMasterDetailView.as_view(), name="group_master_detail"),
    path("new/group_master/", views.GroupMasterCreateView.as_view(), name="group_master_create"),
    path("group_master/<str:pk>/update/", views.GroupMasterUpdateView.as_view(), name="group_master_update"),
    path("group_master/<str:pk>/delete/", views.GroupMasterDeleteView.as_view(), name="group_master_delete"),
    # account
    path("accounts/", views.AccountListView.as_view(), name="account_list"),
    path("account/<str:pk>/", views.AccountDetailView.as_view(), name="account_detail"),
    path("new/account/", views.AccountCreateView.as_view(), name="account_create"),
    path("account/<str:pk>/update/", views.AccountUpdateView.as_view(), name="account_update"),
    path("account/<str:pk>/delete/", views.AccountDeleteView.as_view(), name="account_delete"),
]
