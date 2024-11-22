from django.test import TestCase, tag

from ..factories import AccountFactory
from ..models import Account


class AccountFactoryTest(TestCase):
    @tag("z")
    def test_create_single_object(self):
        account = AccountFactory.create()

        self.assertIsInstance(account, Account)
        self.assertEqual(Account.objects.count(), 1)

    # @tag('x')
    def test_create_multiple_objects(self):
        AccountFactory.create_batch(10)
        self.assertEqual(Account.objects.count(), 10)
