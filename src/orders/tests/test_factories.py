from django.test import TestCase, tag
from icecream import ic

from ..factories import (
    AddressFactory,
    OrderFactory,
    OrderItemFactory,
    ShippingTypeFactory,
)
from ..models import Address, Order, OrderItem, ShippingType


class AddressFactoryTest(TestCase):
    @tag("x")
    def test_create_single_object(self):
        address = AddressFactory.create()
        ic(address.state)

        self.assertIsInstance(address, Address)
        self.assertEqual(Address.objects.count(), 1)

    def test_create_multiple_objects(self):
        address = AddressFactory.create_batch(10)
        ic(address)
        self.assertEqual(Address.objects.count(), 10)


class ShippingTypeFactoryTest(TestCase):
    # @tag('x')
    def test_create_single_object(self):
        shipping_type = ShippingTypeFactory.create()
        ic(shipping_type)

        self.assertIsInstance(shipping_type, ShippingType)
        self.assertEqual(ShippingType.objects.count(), 1)

    def test_create_multiple_objects(self):
        shipping_type = ShippingTypeFactory.create_batch(10)
        ic(shipping_type)
        self.assertEqual(ShippingType.objects.count(), 10)


class OrderFactoryTest(TestCase):
    # @tag('x')
    def test_create_single_object(self):
        order = OrderFactory.create()
        ic(order)

        self.assertIsInstance(order, Order)
        self.assertEqual(Order.objects.count(), 1)

    def test_create_multiple_objects(self):
        order = OrderFactory.create_batch(10)
        ic(order)

        self.assertEqual(Order.objects.count(), 10)


class OrderItemFactoryTest(TestCase):
    # @tag("x")
    def test_create_single_object(self):
        order_item = OrderItemFactory.create()
        ic(order_item)

        self.assertIsInstance(order_item, OrderItem)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_create_multiple_objects(self):
        order_item = OrderItemFactory.create_batch(10)
        ic(order_item)

        self.assertEqual(OrderItem.objects.count(), 10)
