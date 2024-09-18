from http import HTTPStatus

from django.shortcuts import reverse
from django.test import TestCase, tag

from users.factories import AccountFactory


class TestCartsView(TestCase):
    def setUp(self):
        self.account = AccountFactory.create()
        self.admin_dashboard_list_view_url = reverse("dashboards:admin-dashboard-list")

    @tag("z")
    def test_admin_dashboard_list_view_when_logged_in(self):
        self.client.force_login(self.account)
        response = self.client.get(self.admin_dashboard_list_view_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "dashboards/dashboard.html")

    # @tag('x')
    def test_admin_dashboard_list_view_when_not_logged_in(self):
        response = self.client.get(self.admin_dashboard_list_view_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = (
            f"{reverse('users:login')}?next={self.admin_dashboard_list_view_url}"
        )
        self.assertRedirects(response, expected_url)
