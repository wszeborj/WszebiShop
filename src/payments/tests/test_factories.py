from django.test import TestCase, tag
from icecream import ic

from ..factories import PaymentFactory
from ..models import Payment


class PaymentFactoryTest(TestCase):
    # @tag("x")
    def test_create_single_object(self):
        payment = PaymentFactory.create()
        ic(payment)

        self.assertIsInstance(payment, Payment)
        self.assertEqual(Payment.objects.count(), 1)

    def test_create_multiple_objects(self):
        payment = PaymentFactory.create_batch(10)
        ic(payment)
        self.assertEqual(Payment.objects.count(), 10)
