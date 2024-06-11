from django.urls import path

from . import views

app_name = "dashboards"

urlpatterns = [
    path("", views.AdminDashboardListView.as_view(), name="admin-dashboard-list"),
]
