from django.urls import path

from . import views
from .dash_apps import app  # noqa

app_name = "dashboards"

urlpatterns = [
    path("", views.AdminDashboardListView.as_view(), name="dashboard-list"),
]
