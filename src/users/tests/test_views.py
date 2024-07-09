from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, tag
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from users.factories import AccountFactory
from users.models import Account


class TestUserViews(TestCase):
    def setUp(self):
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.profile_url = reverse("users:profile-update")

    # @tag('x')
    def test_register_view_POST(self):
        account = AccountFactory.build()
        account_data = {
            "username": account.username,
            "first_name": "test_name",
            "last_name": "test_last_name",
            "email": "test@test.com",
            "password": "Test.Password",
            "phone": "1234567890",
            "birth_date": "1990-12-04",
        }

        response = self.client.post(
            path=self.register_url, data=account_data, follow=True
        )

        self.assertTemplateUsed(response, "users/register.html")
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Account.objects.count(), 1)
        self.assertFalse(Account.objects.first().is_active)

    # @tag('x')
    def test_profile_update_view_GET(self):
        account = AccountFactory.create()
        self.client.login(
            username=account.username, password=account.password
        )  # force_login

        response = self.client.get(path=self.profile_url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")

    # @tag('x')
    def test_activate_view_GET(self):
        account = AccountFactory(is_active=False)
        uid = urlsafe_base64_encode(force_bytes(account.pk))
        token = default_token_generator.make_token(account)
        activate_url = reverse("users:activate", args=[uid, token])

        response = self.client.get(path=activate_url, follow=True)
        self.assertEquals(response.status_code, 302)
        account.refresh_from_db()
        self.assertTrue(account.is_active)
