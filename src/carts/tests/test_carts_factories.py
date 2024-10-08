from django.test import TestCase, tag
from icecream import ic

from shop.models import Product
from users.tests.utils import ic_all_attributes

from ..factories import CartItemFactory
from ..models import CartItem


class CartItemFactoryTest(TestCase):
    @tag("z")
    def test_create_single_object(self):
        cart_item = CartItemFactory.create()
        ic(cart_item)
        ic_all_attributes(cart_item)

        self.assertIsInstance(cart_item, CartItem)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(Product.objects.count(), 1)
        self.assertIsNotNone(cart_item.product)
        self.assertEqual(cart_item.quantity, 1)
        self.assertIsNotNone(cart_item.account)
        self.assertIsNotNone(cart_item.created_at)

    def test_create_multiple_objects(self):
        cart_item = CartItemFactory.create_batch(10)
        ic(cart_item)
        self.assertEqual(CartItem.objects.count(), 10)
