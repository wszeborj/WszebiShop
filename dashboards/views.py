from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AdminDashboardListView(LoginRequiredMixin, TemplateView):
    template_name = "dashboards/dashboard.html"
