from django.test import TestCase

from shop.models import Product

from ..factories import CartItemFactory
from ..models import CartItem


class CartItemFactoryTest(TestCase):
    def test_create_single_object(self):
        cart_item = CartItemFactory.create()

        self.assertIsInstance(cart_item, CartItem)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(Product.objects.count(), 1)
        self.assertIsNotNone(cart_item.product)
        self.assertEqual(cart_item.quantity, 1)
        self.assertIsNotNone(cart_item.account)
        self.assertIsNotNone(cart_item.created_at)

    def test_create_multiple_objects(self):
        CartItemFactory.create_batch(10)
        self.assertEqual(CartItem.objects.count(), 10)
