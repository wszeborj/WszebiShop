from django.test import TestCase, tag
from icecream import ic

from ..factories import AccountFactory
from ..models import Account


class AccountFactoryTest(TestCase):
    # @tag('x')
    def test_create_single_object(self):
        account = AccountFactory.create()
        ic(account)

        self.assertIsInstance(account, Account)
        self.assertEqual(Account.objects.count(), 1)

    # @tag('x')
    def test_create_multiple_objects(self):
        accounts = AccountFactory.create_batch(10)

        for account in accounts:
            ic(account.first_name)
        self.assertEqual(Account.objects.count(), 10)
