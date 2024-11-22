from http import HTTPStatus

from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import TestCase, tag

from shop.factories import ProductFactory
from users.factories import AccountFactory

from ..factories import CartItemFactory
from ..models import CartItem


class TestCartsView(TestCase):
    def setUp(self):
        self.account = AccountFactory.create()
        self.client.force_login(self.account)
        self.product1 = ProductFactory.create(seller=self.account, in_stock=10)
        self.product2 = ProductFactory.create(seller=self.account, in_stock=5)
        self.product3 = ProductFactory.create(seller=self.account, in_stock=3)
        self.cart_item1 = CartItemFactory.create(
            account=self.account, product=self.product1, quantity=3
        )
        self.cart_item2 = CartItemFactory.create(
            account=self.account, product=self.product2, quantity=1
        )

    @tag("z")
    def test_cart_list_view_GET(self):
        cart_list_view_url = reverse(viewname="carts:cart-details")
        response = self.client.get(path=cart_list_view_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "carts/cart_details.html")
        self.assertIn("cart_items", response.context)
        self.assertIn("total_price", response.context)
        self.assertIn("update_quantity_form", response.context)
        self.assertIn("one_seller", response.context)
        self.assertEqual(len(response.context["cart_items"]), 2)
        self.assertEqual(len(response.context["cart_items"]), CartItem.objects.count())
        self.assertEqual(
            response.context["total_price"],
            self.product1.unit_price * self.cart_item1.quantity
            + self.product2.unit_price * self.cart_item2.quantity,
        )
        self.assertTrue(response.context["one_seller"])

    # @tag('x')
    def test_add_to_cart_view_new_product_will_create_new_cart_item_POST(self):
        add_to_cart_url = reverse(viewname="carts:add-to-cart", args=[self.product3.id])
        response = self.client.post(path=add_to_cart_url)

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 3)
        self.assertEquals(CartItem.objects.last().product, self.product3)
        self.assertEquals(CartItem.objects.last().quantity, 1)
        self.assertEquals(CartItem.objects.last().account, self.account)

    # @tag('x')
    def test_add_to_cart_view_adding_existing_product_in_cart_will_increment_quantity_in_cart_item_POST(
        self,
    ):
        add_to_cart_url = reverse(viewname="carts:add-to-cart", args=[self.product2.id])
        response = self.client.post(path=add_to_cart_url)

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 2)
        self.assertEquals(CartItem.objects.last().product, self.product2)
        self.assertEquals(CartItem.objects.last().quantity, 2)
        self.assertEquals(CartItem.objects.last().account, self.account)

    # @tag('x')
    def test_remove_from_cart_view_removing_last_product_in_cart_item_will_delete_cart_item_POST(
        self,
    ):
        remove_from_cart_url = reverse(
            viewname="carts:remove-from-cart", args=[self.product2.id]
        )
        response = self.client.post(path=remove_from_cart_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEquals(CartItem.objects.last().product, self.product1)

    # @tag('x')
    def test_remove_from_cart_view_removing_product_in_cart_item_will_decrement_cart_item_quantity_POST(
        self,
    ):
        remove_from_cart_url = reverse(
            viewname="carts:remove-from-cart", args=[self.product1.id]
        )
        response = self.client.post(path=remove_from_cart_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 2)
        self.assertEquals(CartItem.objects.first().product, self.product1)
        self.assertEquals(CartItem.objects.first().quantity, 2)
        self.assertEquals(CartItem.objects.first().account, self.account)

    # @tag('x')
    def test_remove_all_view_remove_all_cart_items_from_cart_POST(self):
        remove_all_url = reverse("carts:remove-all")
        response = self.client.post(path=remove_all_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 0)

    # @tag("x")
    def test_remove_item_view_removes_one_cart_item_POST(self):
        remove_item_url = reverse(
            viewname="carts:remove-item", args=[self.cart_item1.id]
        )
        response = self.client.post(path=remove_item_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEquals(CartItem.objects.first().product, self.product2)

    # @tag('x')
    def test_update_cart_vew_update_quantity_to_zero_will_remove_cart_item_POST(self):
        update_cart_url = reverse(
            viewname="carts:update-quantity", args=[self.product1.id]
        )
        response = self.client.post(path=update_cart_url, data={"quantity": 0})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEquals(CartItem.objects.first(), self.cart_item2)
        self.assertEquals(CartItem.objects.first().product, self.product2)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Quantity updated. Item removed")

    # @tag('x')
    def test_update_cart_vew_update_quantity_to_exceed_product_in_stock_will_not_change_quantity_in_cart_item_POST(
        self,
    ):
        update_cart_url = reverse(
            viewname="carts:update-quantity", args=[self.product1.id]
        )
        response = self.client.post(path=update_cart_url, data={"quantity": 11})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 2)
        self.assertEquals(self.cart_item1.quantity, 3)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), f"Only {self.product1.in_stock} items available"
        )

    # @tag('x')
    def test_update_cart_vew_update_quantity_with_proper_value_POST(self):
        update_cart_url = reverse(
            viewname="carts:update-quantity", args=[self.product1.id]
        )
        response = self.client.post(path=update_cart_url, data={"quantity": 1})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 2)
        self.cart_item1.refresh_from_db()
        self.assertEquals(self.cart_item1.quantity, 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Quantity updated.")

    # @tag("x")
    def test_update_cart_vew_update_quantity_with_negative_value_should_not_be_updated_POST(
        self,
    ):
        update_cart_url = reverse(
            viewname="carts:update-quantity", args=[self.product1.id]
        )
        response = self.client.post(path=update_cart_url, data={"quantity": -1})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(CartItem.objects.count(), 2)
        self.cart_item1.refresh_from_db()
        self.assertEquals(self.cart_item1.quantity, 3)
