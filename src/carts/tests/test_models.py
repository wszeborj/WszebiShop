from django.test import TestCase
from django.urls import reverse

from shop.factories import ProductFactory

from ..factories import CartItemFactory


class TestCartsModel(TestCase):
    def setUp(self):
        self.product1 = ProductFactory.create(unit_price=1.11)
        self.cart_item1 = CartItemFactory.create(product=self.product1, quantity=3)

    def test_get_absolute_url(self):
        expected_url = reverse("carts:cart-details")
        self.assertEqual(self.cart_item1.get_absolute_url(), expected_url)

    def test_total_product_cost(self):
        expected_cost = 3.33
        self.assertEqual(self.cart_item1.total_product_cost, expected_cost)
