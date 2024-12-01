from django.test import TestCase

from ..factories import AccountFactory
from ..models import Account


class AccountFactoryTest(TestCase):
    def test_create_single_object(self):
        account = AccountFactory.create()

        self.assertIsInstance(account, Account)
        self.assertEqual(Account.objects.count(), 1)

    def test_create_multiple_objects(self):
        AccountFactory.create_batch(10)
        self.assertEqual(Account.objects.count(), 10)
