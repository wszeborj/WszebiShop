from django.test import TestCase, tag
from icecream import ic

from shop.factories import ProductFactory
from shop.models import Product
from users.factories import AccountFactory
from users.models import Account

from ..factories import (
    AddressFactory,
    OrderFactory,
    OrderItemFactory,
    ShippingTypeFactory,
)
from ..models import Address, Order, OrderItem, ShippingType


class AddressFactoryTest(TestCase):
    @tag("z")
    def test_create_single_object(self):
        address = AddressFactory.create()
        # ic(address)
        # ic_all_attributes(address)

        self.assertIsInstance(address, Address)
        self.assertEqual(Address.objects.count(), 1)
        self.assertIsInstance(address.account, Account)
        self.assertEqual(Account.objects.count(), 1)
        self.assertIsNotNone(address.first_name)
        self.assertIsNotNone(address.last_name)
        self.assertIsNotNone(address.street)
        self.assertIsNotNone(address.phone)
        self.assertIsNotNone(address.city)
        self.assertIsNotNone(address.postal_code)
        self.assertIsNotNone(address.state)
        self.assertIsNotNone(address.country)
        self.assertIsNotNone(address.created_at)

    def test_create_multiple_objects(self):
        AddressFactory.create_batch(10)
        self.assertEqual(Address.objects.count(), 10)


class ShippingTypeFactoryTest(TestCase):
    # @tag('x')
    def test_create_single_object(self):
        shipping_type = ShippingTypeFactory.create()

        self.assertIsInstance(shipping_type, ShippingType)
        self.assertEqual(ShippingType.objects.count(), 1)
        self.assertIsNotNone(shipping_type.type)
        self.assertGreater(shipping_type.price, 0)

    def test_create_multiple_objects(self):
        shipping_type = ShippingTypeFactory.create_batch(10)
        ic(shipping_type)
        self.assertEqual(ShippingType.objects.count(), 10)


class OrderFactoryTest(TestCase):
    @tag("x")
    def test_create_single_object(self):
        order = OrderFactory.create()
        # ic(order)
        # ic_all_attributes(order)

        self.assertIsInstance(order, Order)
        self.assertEqual(Order.objects.count(), 1)
        self.assertIsNotNone(order.status)
        self.assertIsNotNone(order.shipping_status)
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.update_at)
        self.assertIsNotNone(order.buyer)
        self.assertIsInstance(order.buyer, Account)
        self.assertEqual(Account.objects.count(), 2)
        self.assertIsNotNone(order.address)
        self.assertIsInstance(order.address, Address)
        self.assertEqual(Address.objects.count(), 1)
        self.assertIsNotNone(order.shipping_type)
        self.assertIsInstance(order.shipping_type, ShippingType)
        self.assertEqual(ShippingType.objects.count(), 1)
        self.assertGreater(order.total_price_with_shipping, 0)

    def test_create_multiple_objects(self):
        OrderFactory.create_batch(10)
        self.assertEqual(Order.objects.count(), 10)


class OrderItemFactoryTest(TestCase):
    def setUp(self):
        self.seller_account = AccountFactory.create()
        self.buyer_account = AccountFactory.create()
        self.product1 = ProductFactory.create(seller=self.seller_account)

    # @tag("x")
    def test_create_single_object(self):
        order_item = OrderItemFactory.create(product=self.product1)

        self.assertIsInstance(order_item, OrderItem)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertIsNotNone(order_item.product)
        self.assertIsInstance(order_item.product, Product)
        self.assertEqual(order_item.quantity, 1)
        self.assertIsNotNone(order_item.account)
        self.assertIsInstance(order_item.account, Account)
        self.assertEqual(Account.objects.count(), 2)
        self.assertIsNotNone(order_item.created_at)
        self.assertIsNotNone(order_item.update_at)
        self.assertIsNotNone(order_item.order)
        self.assertIsInstance(order_item.order, Order)
        self.assertEqual(Order.objects.count(), 1)

    def test_create_multiple_objects(self):
        OrderItemFactory.create_batch(10)
        self.assertEqual(OrderItem.objects.count(), 10)
