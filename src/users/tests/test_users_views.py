from datetime import datetime
from http import HTTPStatus

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, tag
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.factories import AccountFactory
from users.models import Account


class TestUserViews(TestCase):
    def setUp(self):
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.profile_url = reverse("users:profile-update")

    @tag("z")
    def test_register_view_valid_POST(self):
        birth_date_str = "1990-12-04"
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        account_data = {
            "username": "test_username",
            "first_name": "test_name",
            "last_name": "test_last_name",
            "email": "test@test.com",
            "password1": "Test.Password",
            "password2": "Test.Password",
            "phone": "+12123456789",
            "birth_date": birth_date,
        }

        response = self.client.post(
            path=self.register_url, data=account_data, follow=True
        )

        self.assertRedirects(response, self.login_url)
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Account.objects.count(), 1)
        self.assertEquals(Account.objects.first().username, account_data["username"])
        self.assertEquals(
            Account.objects.first().first_name, account_data["first_name"]
        )
        self.assertEquals(Account.objects.first().last_name, account_data["last_name"])
        self.assertEquals(Account.objects.first().email, account_data["email"])
        self.assertEquals(Account.objects.first().phone, account_data["phone"])
        self.assertEquals(
            Account.objects.first().birth_date, account_data["birth_date"]
        )
        self.assertFalse(Account.objects.first().is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "Activation link to your account on Wszebishop"
        )

    # @tag('x')
    def test_register_view_invalid_POST(self):
        birth_date_str = "1990-12-04"
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        account_data = {
            "username": "test_username",
            "first_name": "test_name",
            "last_name": "test_last_name",
            "email": "test@test.com",
            "password1": "Test.Password",
            "password2": "Test.Password*",
            "phone": "+12123456789",
            "birth_date": birth_date,
        }

        response = self.client.post(
            path=self.register_url, data=account_data, follow=True
        )

        self.assertTemplateUsed(response, "users/register.html")
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Account.objects.count(), 0)
        self.assertContains(
            response,
            "Something went wrong! Check your email and password and try again.",
        )
        self.assertEqual(len(mail.outbox), 0)

    # @tag('x')
    def test_profile_update_view_POST(self):
        account = AccountFactory.create()
        self.client.force_login(account)

        new_data = {
            "username": "updated_username",
            "email": "updatedtest@test.com",
            "phone": "999876543210",
        }

        response = self.client.get(path=self.profile_url, data=new_data, follow=True)
        account.refresh_from_db()
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertEquals(account.username, new_data["username"])
        self.assertEquals(account.email, new_data["email"])
        self.assertEquals(account.phone, new_data["phone"])

    # @tag('x')
    def test_activate_view_success_GET(self):
        account = AccountFactory(is_active=False)
        uid = urlsafe_base64_encode(force_bytes(account.pk))
        token = default_token_generator.make_token(account)
        activate_url = reverse("users:activate", args=[uid, token])

        response = self.client.get(path=activate_url, args=[uid, token], follow=True)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        account.refresh_from_db()
        self.assertTrue(account.is_active)
        self.assertContains(response, "Your account has been activated successfully!")

    # @tag('x')
    def test_activate_view_failure_GET(self):
        uid = "invalid_uid"
        token = "invalid_token"
        activate_url = reverse("users:activate", args=[uid, token])

        response = self.client.get(path=activate_url, args=[uid, token], follow=True)

        self.assertContains(response, "Activation link is invalid!")
        self.assertEquals(response.status_code, HTTPStatus.OK)
