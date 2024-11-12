from http import HTTPStatus

from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import TestCase, tag

from carts.factories import CartItemFactory
from carts.models import CartItem
from orders.factories import (
    AddressFactory,
    OrderFactory,
    OrderItemFactory,
    ShippingTypeFactory,
)
from shop.factories import ProductFactory
from users.factories import AccountFactory

from ..forms import AddressForm
from ..models import Address, Order


class TestOrdersView(TestCase):
    def setUp(self):
        self.account = AccountFactory.create()
        self.other_user = AccountFactory.create()

        self.product1 = ProductFactory.create(seller=self.account, in_stock=10)
        self.product2 = ProductFactory.create(seller=self.account, in_stock=5)
        self.product3 = ProductFactory.create(seller=self.account, in_stock=3)
        self.cart_item1 = CartItemFactory.create(
            account=self.account, product=self.product1, quantity=3
        )
        self.cart_item2 = CartItemFactory.create(
            account=self.account, product=self.product2, quantity=1
        )
        self.addresses = AddressFactory.create_batch(2, account=self.account)
        self.shipping_types = ShippingTypeFactory.create_batch(2)

        self.login_url = reverse("users:login")
        self.order_confirmation_list_view_url = reverse("orders:order-confirmation")
        self.add_address_url = reverse(viewname="orders:add-address")
        self.orders_list_url = reverse(viewname="orders:orders-list")
        self.sales_list_url = reverse(viewname="orders:sales-list")

    def test_order_confirmation_list_view_logged_in_GET(self):
        self.client.force_login(self.account)
        response = self.client.get(self.order_confirmation_list_view_url)

        self.assertIn("cart_items", response.context)
        self.assertIn("total_price", response.context)
        self.assertIn("shipping_addresses", response.context)
        self.assertIn("shipping_types", response.context)
        self.assertIn("selected_shipping_type", response.context)
        self.assertIn("selected_shipping_address", response.context)
        self.assertIn("total_price_with_shipping", response.context)

    def test_order_confirmation_list_view_not_logged_in_GET(self):
        response = self.client.get(self.order_confirmation_list_view_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{self.login_url}?next={self.order_confirmation_list_view_url}"
        self.assertRedirects(response, expected_url)

    def test_product_to_order_view_should_add_product_to_cart_and_proceed_to_order_POST(
        self,
    ):
        self.client.force_login(self.account)
        product_to_order_url = reverse(
            viewname="orders:product-to-order", args=[self.product3.id]
        )
        response = self.client.post(product_to_order_url)

        self.assertRedirects(response, self.order_confirmation_list_view_url)
        self.assertEqual(CartItem.objects.count(), 3)
        self.assertTrue(
            CartItem.objects.filter(product=self.product3, account=self.account)
        )

    def test_add_address_view_logged_in_valid_data_new_address_should_be_added_POST(
        self,
    ):
        self.client.force_login(self.account)
        new_address = {
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "street": "test_street",
            "phone": "+12125552368",
            "city": "test_city",
            "postal_code": "99-999",
            "state": "test_state",
            "country": "test_country",
        }
        response = self.client.post(path=self.add_address_url, data=new_address)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.order_confirmation_list_view_url)
        self.assertEqual(Address.objects.count(), 3)

        tested_address = Address.objects.get(first_name="test_first_name")
        self.assertEqual(tested_address.account, self.account)
        self.assertEqual(tested_address.first_name, new_address["first_name"])
        self.assertEqual(tested_address.last_name, new_address["last_name"])
        self.assertEqual(tested_address.street, new_address["street"])
        self.assertEqual(tested_address.first_name, new_address["first_name"])
        self.assertEqual(tested_address.phone, new_address["phone"])
        self.assertEqual(tested_address.city, new_address["city"])
        self.assertEqual(tested_address.postal_code, new_address["postal_code"])
        self.assertEqual(tested_address.state, new_address["state"])
        self.assertEqual(tested_address.country, new_address["country"])
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "New address added")

    def test_add_address_view_logged_in_invalid_data_new_address_should_not_be_added_POST(
        self,
    ):
        self.client.force_login(self.account)
        new_address = {
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "street": "test_street",
            "phone": "+12125552368",
            "city": "test_city",
            "postal_code": "invalid_code",
            "state": "test_state",
            "country": "test_country",
        }
        response = self.client.post(path=self.add_address_url, data=new_address)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Address.objects.count(), 2)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Some values in address form were wrong")

    def test_add_address_view_not_logged_in_POST(self):
        new_address = {
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "street": "test_street",
            "phone": "+12125552368",
            "city": "test_city",
            "postal_code": "99-999",
            "state": "test_state",
            "country": "test_country",
        }
        response = self.client.post(path=self.add_address_url, data=new_address)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{reverse('users:login')}?next={self.add_address_url}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(Address.objects.count(), 2)

    def test_add_address_view_logged_in_GET(self):
        self.client.force_login(self.account)
        response = self.client.get(path=self.add_address_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "orders/add-address.html")
        self.assertIsInstance(response.context["form"], AddressForm)


class TestOrdersListView(TestCase):
    def setUp(self):
        self.account = AccountFactory.create()
        self.other_user = AccountFactory.create()

        self.product1 = ProductFactory.create(seller=self.account, in_stock=10)
        self.product2 = ProductFactory.create(seller=self.account, in_stock=5)
        self.product3 = ProductFactory.create(seller=self.account, in_stock=3)
        self.cart_item1 = CartItemFactory.create(
            account=self.account, product=self.product1, quantity=3
        )
        self.cart_item2 = CartItemFactory.create(
            account=self.account, product=self.product2, quantity=1
        )
        self.addresses = AddressFactory.create_batch(2, account=self.account)
        self.shipping_types = ShippingTypeFactory.create_batch(2)

        self.order1 = OrderFactory.create(buyer=self.account, status="AWAITING_PAYMENT")
        self.order2 = OrderFactory.create(buyer=self.account, status="PAID")
        self.order3 = OrderFactory.create(buyer=self.other_user, status="PAID")

        self.login_url = reverse("users:login")
        self.order_confirmation_list_view_url = reverse("orders:order-confirmation")
        self.add_address_url = reverse(viewname="orders:add-address")
        self.orders_list_url = reverse(viewname="orders:orders-list")
        self.sales_list_url = reverse(viewname="orders:sales-list")

    def test_order_list_view_logged_in_without_filter_GET(self):
        self.client.force_login(self.account)

        response = self.client.get(self.orders_list_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "orders/orders_list.html")
        self.assertIn(self.order1, response.context["order_items"])
        self.assertIn(self.order2, response.context["order_items"])
        self.assertNotIn(self.order3, response.context["order_items"])

    @tag("z")
    def test_order_list_view_logged_in_with_filter_GET(self):
        self.client.force_login(self.account)

        response = self.client.get(
            path=self.orders_list_url, data={"status": "AWAITING_PAYMENT"}
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "orders/orders_list.html")
        self.assertIn(self.order1, response.context["order_items"])
        self.assertNotIn(self.order2, response.context["order_items"])
        self.assertNotIn(self.order3, response.context["order_items"])

        response = self.client.get(path=self.orders_list_url, data={"status": "PAID"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "orders/orders_list.html")
        self.assertNotIn(self.order1, response.context["order_items"])
        self.assertIn(self.order2, response.context["order_items"])
        self.assertNotIn(self.order3, response.context["order_items"])

    # @tag('x')
    def test_order_list_view_not_logged_in_GET(self):
        response = self.client.get(self.orders_list_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{reverse('users:login')}?next={self.orders_list_url}"
        self.assertRedirects(response, expected_url)


class TestSalesListView(TestCase):
    def setUp(self):
        self.account = AccountFactory.create()
        self.other_user = AccountFactory.create()

        self.product1 = ProductFactory.create(seller=self.account)
        self.product2 = ProductFactory.create(seller=self.account)
        self.product3 = ProductFactory.create(seller=self.other_user)

        self.order1 = OrderFactory.create(status="AWAITING_PAYMENT")
        self.order2 = OrderFactory.create(status="PAID")
        self.order3 = OrderFactory.create(status="AWAITING_PAYMENT")

        self.order_item1 = OrderItemFactory.create(
            order=self.order1, product=self.product1
        )
        self.order_item2 = OrderItemFactory.create(
            order=self.order2, product=self.product2
        )
        self.order_item3 = OrderItemFactory.create(
            order=self.order3, product=self.product3
        )

        self.login_url = reverse("users:login")
        self.sales_list_url = reverse(viewname="orders:sales-list")

    # @tag('x')
    def test_sales_list_view_logged_in_without_filter_GET(self):
        self.client.force_login(self.account)
        response = self.client.get(self.sales_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/orders_list.html")
        self.assertIn(self.order1, response.context["order_items"])
        self.assertIn(self.order2, response.context["order_items"])
        self.assertNotIn(self.order3, response.context["order_items"])

    # @tag('x')
    def test_sales_list_view_logged_in_with_filter_GET(self):
        self.client.force_login(self.account)
        response = self.client.get(
            path=self.sales_list_url, data={"status": "AWAITING_PAYMENT"}
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "orders/orders_list.html")
        self.assertIn(self.order1, response.context["order_items"])
        self.assertNotIn(self.order2, response.context["order_items"])
        self.assertNotIn(self.order3, response.context["order_items"])

        response = self.client.get(path=self.sales_list_url, data={"status": "PAID"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "orders/orders_list.html")
        self.assertNotIn(self.order1, response.context["order_items"])
        self.assertIn(self.order2, response.context["order_items"])
        self.assertNotIn(self.order3, response.context["order_items"])

    # @tag('x')
    def test_sales_list_view_not_logged_in_GET(self):
        response = self.client.get(self.sales_list_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{reverse('users:login')}?next={self.sales_list_url}"
        self.assertRedirects(response, expected_url)


class TestOrderDetailView(TestCase):
    def setUp(self):
        self.account = AccountFactory.create()
        self.other_user = AccountFactory.create()

        self.product1 = ProductFactory.create(seller=self.account)
        self.product2 = ProductFactory.create(seller=self.other_user)

        self.order1 = OrderFactory.create(status="AWAITING_PAYMENT")
        self.order2 = OrderFactory.create(status="PAID")
        self.order3 = OrderFactory.create(status="AWAITING_PAYMENT")

        self.order_item1 = OrderItemFactory.create(
            order=self.order1, product=self.product1
        )
        self.order_item2 = OrderItemFactory.create(
            order=self.order2, product=self.product2
        )
        self.order_item3 = OrderItemFactory.create(
            order=self.order3, product=self.product1
        )

        self.login_url = reverse("users:login")
        self.order_detail_url = reverse(
            viewname="orders:order-details", args=[self.order1.id]
        )

    # @tag('x')
    def test_order_detail_view_logged_in_GET(self):
        self.client.force_login(self.account)

        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/order_detail.html")
        self.assertEqual(response.context["order"], self.order1)

    # @tag('x')
    def test_order_detail_view_logged_in_other_user_should_return_not_found_GET(self):
        self.client.force_login(self.other_user)

        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # @tag('x')
    def test_order_detail_view_not_logged_in_GET(self):
        response = self.client.get(self.order_detail_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{reverse('users:login')}?next={self.order_detail_url}"
        self.assertRedirects(response, expected_url)


class UpdateOrderStatusTests(TestCase):
    def setUp(self):
        self.account = AccountFactory.create()
        self.order = OrderFactory.create(
            shipping_status=Order.OrderShippingStatus.NEW, buyer=self.account
        )

        self.update_status_url = reverse(
            "orders:order-update-status", args=[self.order.id]
        )

    # @tag('x')
    def test_order_update_status_view_logged_in_POST(self):
        self.client.force_login(self.account)
        new_status = Order.OrderShippingStatus.SHIPPED
        status_data = {"order_shipping_status": new_status}
        response = self.client.post(path=self.update_status_url, data=status_data)

        self.order.refresh_from_db()
        self.assertEqual(self.order.shipping_status, new_status)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse(viewname="orders:order-details", args=[self.order.id])
        )

    # @tag('x')
    def test_order_update_status_view_not_logged_in_POST(self):
        response = self.client.post(self.update_status_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        expected_url = f"{reverse('users:login')}?next={self.update_status_url}"
        self.assertRedirects(response, expected_url)
