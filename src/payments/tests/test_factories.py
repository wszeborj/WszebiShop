from django.test import TestCase, tag
from icecream import ic

from orders.models import Order
from users.models import Account

from ..factories import PaymentFactory
from ..models import Payment


class PaymentFactoryTest(TestCase):
    @tag("z")
    def test_create_single_object(self):
        payment = PaymentFactory.create()
        ic(payment)

        self.assertIsInstance(payment, Payment)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertIsInstance(payment.user, Account)
        self.assertEqual(Account.objects.count(), 1)
        self.assertIsInstance(payment.order, Order)
        self.assertEqual(Order.objects.count(), 1)
        self.assertIsNotNone(payment.user)
        self.assertIsNotNone(payment.order)
        self.assertGreater(payment.price, 0)
        self.assertIsNotNone(payment.created_at)
        self.assertIsNotNone(payment.state)

    def test_create_multiple_objects(self):
        payment = PaymentFactory.create_batch(10)
        ic(payment)
        self.assertEqual(Payment.objects.count(), 10)
