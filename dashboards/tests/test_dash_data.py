from datetime import date, timedelta
from typing import Tuple, Union

import pandas as pd
from django.test import TestCase
from django.utils import timezone

from dashboards.dash_data import DashData
from orders.factories import OrderFactory, OrderItemFactory
from orders.models import Order, OrderItem
from shop.factories import CategoryFactory, ProductFactory
from users.factories import AccountFactory


class DashDataTestCase(TestCase):
    def setUp(self):
        self.staff_user = AccountFactory.create(username="admin", is_staff=True)
        self.regular_user = AccountFactory.create(username="user", is_staff=False)
        self.regular_user2 = AccountFactory.create(username="user2", is_staff=False)
        self.regular_user3 = AccountFactory.create(username="user3", is_staff=False)

        self.category = CategoryFactory.create(name="Electronics")
        self.category2 = CategoryFactory.create(name="Clothes")

        self.product = ProductFactory.create(
            name="Smartphone",
            category=self.category,
            unit_price=500,
        )

        self.product2 = ProductFactory.create(
            name="Jacket",
            category=self.category2,
            unit_price=1000,
        )

        self.today = timezone.now()
        self.yesterday = self.today - timedelta(days=1)
        # order_1
        self.order_1 = OrderFactory.create(
            buyer=self.regular_user, status=Order.OrderStatus.PAID
        )
        self.order_item_1 = OrderItemFactory.create(
            order=self.order_1, product=self.product, quantity=2
        )
        OrderItem.objects.filter(pk=self.order_item_1.pk).update(created_at=self.today)
        self.price_of_order1 = self.product.unit_price * self.order_item_1.quantity
        Order.objects.filter(pk=self.order_1.pk).update(
            created_at=self.today, total_price_with_shipping=self.price_of_order1
        )
        # order_2
        self.order_2 = OrderFactory.create(
            buyer=self.regular_user2, status=Order.OrderStatus.PAID
        )
        self.order_item_2 = OrderItemFactory.create(
            order=self.order_2, product=self.product, quantity=1
        )
        OrderItem.objects.filter(pk=self.order_item_2.pk).update(created_at=self.today)
        self.price_of_order2 = self.product.unit_price * self.order_item_2.quantity
        Order.objects.filter(pk=self.order_2.pk).update(
            created_at=self.today, total_price_with_shipping=self.price_of_order2
        )
        # order_3
        self.order_3 = OrderFactory.create(
            buyer=self.regular_user2, status=Order.OrderStatus.PAID
        )
        self.order_item_3 = OrderItemFactory.create(
            order=self.order_3, product=self.product2, quantity=3
        )
        OrderItem.objects.filter(pk=self.order_item_3.pk).update(
            created_at=self.yesterday
        )

        self.price_of_order3 = self.product2.unit_price * self.order_item_3.quantity
        Order.objects.filter(pk=self.order_3.pk).update(
            created_at=self.yesterday, total_price_with_shipping=self.price_of_order3
        )

    def get_data_for_today_and_yesterday(
        self, df: pd.DataFrame, df_name: str
    ) -> Tuple[Union[float, int], Union[float, int]]:
        value_for_today = self.get_value_for_date(
            df=df, df_name=df_name, date=self.today.date()
        )
        value_for_yesterday = self.get_value_for_date(
            df=df, df_name=df_name, date=self.yesterday.date()
        )
        return value_for_today, value_for_yesterday

    def get_value_for_date(
        self, df: pd.DataFrame, df_name: str, date: date
    ) -> Union[float, int]:
        one_element_series = df.loc[df["created_at__date"] == date, df_name]
        value = one_element_series.iloc[0] if not one_element_series.empty else 0
        return value

    def test_get_daily_orders_for_regular_user_should_return_only_one_order_for_today(
        self,
    ):
        df = DashData.get_daily_orders(user=self.regular_user)

        (
            order_count_today,
            order_count_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="order_count")

        self.assertIn("order_count", df.columns)
        self.assertEqual(order_count_today, 1)
        self.assertEqual(order_count_yesterday, 0)

    def test_get_daily_orders_for_regular_user2_should_return_one_order_per_day(self):
        df = DashData.get_daily_orders(user=self.regular_user2)

        (
            order_count_today,
            order_count_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="order_count")

        self.assertIn("order_count", df.columns)
        self.assertEqual(order_count_today, 1)
        self.assertEqual(order_count_yesterday, 1)

    def test_get_daily_orders_for_regular_user3_should_not_return_any_order(self):
        df = DashData.get_daily_orders(user=self.regular_user3)

        self.assertTrue(df.empty)

    def test_get_daily_orders_for_staff_user_should_return_two_order_today_one_order_yesterday(
        self,
    ):
        df = DashData.get_daily_orders(user=self.staff_user)

        (
            order_count_today,
            order_count_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="order_count")

        self.assertIn("order_count", df.columns)
        self.assertEqual(order_count_today, 2)
        self.assertEqual(order_count_yesterday, 1)

    # total_payment ####################################################################################################

    def test_get_daily_total_payments_for_regular_user_should_return_price_for_today(
        self,
    ):
        df = DashData.get_daily_total_payments(user=self.regular_user)

        (
            total_price_today,
            total_price_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="total_payment")

        self.assertIn("total_payment", df.columns)
        self.assertEqual(total_price_today, self.price_of_order1)
        self.assertEqual(total_price_yesterday, 0)

    def test_get_daily_total_payments_for_regular_user2_should_return_price_for_yesterday_and_today(
        self,
    ):
        df = DashData.get_daily_total_payments(user=self.regular_user2)

        (
            total_price_today,
            total_price_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="total_payment")

        self.assertIn("total_payment", df.columns)
        self.assertEqual(total_price_today, self.price_of_order2)
        self.assertEqual(total_price_yesterday, self.price_of_order3)

    def test_get_daily_total_payments_for_regular_user3_should_not_return_any_price(
        self,
    ):
        df = DashData.get_daily_total_payments(user=self.regular_user3)

        self.assertTrue(df.empty)

    def test_get_daily_total_payments_for_staff_user_should_return_one_payment_per_day(
        self,
    ):
        df = DashData.get_daily_total_payments(user=self.staff_user)

        (
            total_price_today,
            total_price_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="total_payment")

        self.assertIn("total_payment", df.columns)
        self.assertEqual(total_price_today, self.price_of_order1 + self.price_of_order2)
        self.assertEqual(total_price_yesterday, self.price_of_order3)

    # total_quantity_order_items_in_day ###################################################################################

    def test_get_daily_order_items_for_regular_user_should_return_quantity_for_today(
        self,
    ):
        df = DashData.get_daily_order_items(user=self.regular_user)

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )

        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(daily_order_items_today, self.order_item_1.quantity)
        self.assertEqual(daily_order_items_yesterday, 0)

    def test_get_daily_order_items_for_regular_user2_should_return_quantity_for_today_and_yesterday(
        self,
    ):
        df = DashData.get_daily_order_items(user=self.regular_user2)

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )

        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(daily_order_items_today, self.order_item_2.quantity)
        self.assertEqual(daily_order_items_yesterday, self.order_item_3.quantity)

    def test_get_daily_order_items_for_regular_user3_should_not_return_any_quantity(
        self,
    ):
        df = DashData.get_daily_order_items(user=self.regular_user3)

        self.assertTrue(df.empty)

    def test_get_daily_order_items_for_staff_user_should_return_quantity_for_today_and_yesterday(
        self,
    ):
        df = DashData.get_daily_order_items(user=self.staff_user)

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )

        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(
            daily_order_items_today,
            self.order_item_1.quantity + self.order_item_2.quantity,
        )
        self.assertEqual(daily_order_items_yesterday, self.order_item_3.quantity)

    def test_get_daily_order_items_for_staff_user_electronics_category_should_return_quantity_for_today(
        self,
    ):
        df = DashData.get_daily_order_items(
            user=self.staff_user, category=self.category
        )

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )

        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(
            daily_order_items_today,
            self.order_item_1.quantity + self.order_item_2.quantity,
        )
        self.assertEqual(daily_order_items_yesterday, 0)

    def test_get_daily_order_items_for_staff_user_clothes_category_should_return_quantity_for_yesterday(
        self,
    ):
        df = DashData.get_daily_order_items(
            user=self.staff_user, category=self.category2
        )

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )

        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(daily_order_items_today, 0)
        self.assertEqual(daily_order_items_yesterday, self.order_item_3.quantity)

    # total_order_item_payment ###################################################################################

    def test_get_daily_order_items_payments_for_regular_user_should_return_price_for_today(
        self,
    ):
        df = DashData.get_daily_order_items_payments(user=self.regular_user)

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(daily_order_items_today, self.price_of_order1)
        self.assertEqual(daily_order_items_yesterday, 0)

    def test_get_daily_order_items_payments_for_regular_user2_should_return_price_for_today_and_yesterday(
        self,
    ):
        df = DashData.get_daily_order_items_payments(user=self.regular_user2)

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(daily_order_items_today, self.price_of_order2)
        self.assertEqual(daily_order_items_yesterday, self.price_of_order3)

    def test_get_daily_order_items_payments_for_regular_user3_should_not_return_any_price(
        self,
    ):
        df = DashData.get_daily_order_items_payments(user=self.regular_user3)

        self.assertTrue(df.empty)

    def test_get_daily_order_items_payments_for_staff_user_should_return_price_for_today_and_yesterday(
        self,
    ):
        df = DashData.get_daily_order_items_payments(user=self.staff_user)

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(
            daily_order_items_today, self.price_of_order1 + self.price_of_order2
        )
        self.assertEqual(daily_order_items_yesterday, self.price_of_order3)

    def test_get_daily_order_items_payments_for_staff_user_electronic_category_should_return_price_for_today(
        self,
    ):
        df = DashData.get_daily_order_items_payments(
            user=self.staff_user, category=self.category
        )

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(
            daily_order_items_today, self.price_of_order1 + self.price_of_order2
        )
        self.assertEqual(daily_order_items_yesterday, 0)

    def test_get_daily_order_items_payments_for_staff_user_clothes_category_should_return_price_for_yesterday(
        self,
    ):
        df = DashData.get_daily_order_items_payments(
            user=self.staff_user, category=self.category2
        )

        (
            daily_order_items_today,
            daily_order_items_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(daily_order_items_today, 0)
        self.assertEqual(daily_order_items_yesterday, self.price_of_order3)

    # combined_order_data ###################################

    def test_get_combined_order_data_for_regular_user_should_return_data_for_today(
        self,
    ):
        df = DashData.get_combined_order_data(user=self.regular_user)

        (
            order_count_today,
            order_count_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="order_count")
        (
            total_payment_today,
            total_payment_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="total_payment")
        (
            avg_order_value_today,
            avg_order_value_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="avg_order_value")
        self.assertIn("order_count", df.columns)
        self.assertEqual(order_count_today, 1)
        self.assertEqual(order_count_yesterday, 0)

        self.assertIn("total_payment", df.columns)
        self.assertEqual(total_payment_today, self.price_of_order1)
        self.assertEqual(total_payment_yesterday, 0)

        self.assertIn("avg_order_value", df.columns)
        self.assertEqual(avg_order_value_today, self.price_of_order1)
        self.assertEqual(avg_order_value_yesterday, 0)

    def test_get_combined_order_data_for_regular_user2_should_return_data_for_today_and_yesterday(
        self,
    ):
        df = DashData.get_combined_order_data(user=self.regular_user2)

        (
            order_count_today,
            order_count_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="order_count")
        (
            total_payment_today,
            total_payment_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="total_payment")
        (
            avg_order_value_today,
            avg_order_value_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="avg_order_value")
        self.assertIn("order_count", df.columns)
        self.assertEqual(order_count_today, 1)
        self.assertEqual(order_count_yesterday, 1)

        self.assertIn("total_payment", df.columns)
        self.assertEqual(total_payment_today, self.price_of_order2)
        self.assertEqual(total_payment_yesterday, self.price_of_order3)

        self.assertIn("avg_order_value", df.columns)
        self.assertEqual(avg_order_value_today, self.price_of_order2)
        self.assertEqual(avg_order_value_yesterday, self.price_of_order3)

    def test_get_combined_order_data_for_regular_user3_should_not_return_any_data(self):
        df = DashData.get_combined_order_data(user=self.regular_user3)

        self.assertTrue(df.empty)
        self.assertIn("created_at__date", df.columns)
        self.assertIn("order_count", df.columns)
        self.assertIn("total_payment", df.columns)
        self.assertIn("avg_order_value", df.columns)

    def test_get_combined_order_data_for_staff_user_should_return_data_for_today_and_yesterday(
        self,
    ):
        df = DashData.get_combined_order_data(user=self.staff_user)

        (
            order_count_today,
            order_count_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="order_count")
        (
            total_payment_today,
            total_payment_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="total_payment")
        (
            avg_order_value_today,
            avg_order_value_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="avg_order_value")
        self.assertIn("order_count", df.columns)
        self.assertEqual(order_count_today, 2)
        self.assertEqual(order_count_yesterday, 1)

        self.assertIn("total_payment", df.columns)
        self.assertEqual(
            total_payment_today, self.price_of_order1 + self.price_of_order2
        )
        self.assertEqual(total_payment_yesterday, self.price_of_order3)

        self.assertIn("avg_order_value", df.columns)
        self.assertEqual(
            avg_order_value_today, (self.price_of_order1 + self.price_of_order2) / 2
        )
        self.assertEqual(avg_order_value_yesterday, self.price_of_order3)

    # combined_order_item_data ########################################

    def test_get_combined_order_item_data_for_regular_user_should_return_data_for_today(
        self,
    ):
        df = DashData.get_combined_order_item_data(user=self.regular_user)

        (
            total_quantity_order_items_in_day_today,
            total_quantity_order_items_in_day_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )
        (
            total_order_item_payment_today,
            total_order_item_payment_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )
        (
            avg_order_item_value_today,
            avg_order_item_value_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="avg_order_item_value")
        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(
            total_quantity_order_items_in_day_today, self.order_item_1.quantity
        )
        self.assertEqual(total_quantity_order_items_in_day_yesterday, 0)

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(total_order_item_payment_today, self.price_of_order1)
        self.assertEqual(total_order_item_payment_yesterday, 0)

        self.assertIn("avg_order_item_value", df.columns)
        self.assertEqual(
            avg_order_item_value_today,
            self.price_of_order1 / self.order_item_1.quantity,
        )
        self.assertEqual(avg_order_item_value_yesterday, 0)

    def test_get_combined_order_item_data_for_regular_user2_should_return_data_for_today_and_yesterday(
        self,
    ):
        df = DashData.get_combined_order_item_data(user=self.regular_user2)

        (
            total_quantity_order_items_in_day_today,
            total_quantity_order_items_in_day_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )
        (
            total_order_item_payment_today,
            total_order_item_payment_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )
        (
            avg_order_item_value_today,
            avg_order_item_value_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="avg_order_item_value")
        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(
            total_quantity_order_items_in_day_today, self.order_item_2.quantity
        )
        self.assertEqual(
            total_quantity_order_items_in_day_yesterday, self.order_item_3.quantity
        )

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(total_order_item_payment_today, self.price_of_order2)
        self.assertEqual(total_order_item_payment_yesterday, self.price_of_order3)

        self.assertIn("avg_order_item_value", df.columns)
        self.assertEqual(
            avg_order_item_value_today,
            self.price_of_order2 / self.order_item_2.quantity,
        )
        self.assertEqual(
            avg_order_item_value_yesterday,
            self.price_of_order3 / self.order_item_3.quantity,
        )

    def test_get_combined_order_item_data_for_regular_user3_should_not_return_any_data(
        self,
    ):
        df = DashData.get_combined_order_item_data(user=self.regular_user3)

        self.assertTrue(df.empty)
        self.assertIn("created_at__date", df.columns)
        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertIn("total_order_item_payment", df.columns)
        self.assertIn("avg_order_item_value", df.columns)

    def test_get_combined_order_item_data_for_staff_user_should_return_data_for_today_and_yesterday(
        self,
    ):
        df = DashData.get_combined_order_item_data(user=self.staff_user)

        (
            total_quantity_order_items_in_day_today,
            total_quantity_order_items_in_day_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )
        (
            total_order_item_payment_today,
            total_order_item_payment_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )
        (
            avg_order_item_value_today,
            avg_order_item_value_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="avg_order_item_value")
        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(
            total_quantity_order_items_in_day_today,
            self.order_item_1.quantity + self.order_item_2.quantity,
        )
        self.assertEqual(
            total_quantity_order_items_in_day_yesterday, self.order_item_3.quantity
        )

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(
            total_order_item_payment_today, self.price_of_order1 + self.price_of_order2
        )
        self.assertEqual(total_order_item_payment_yesterday, self.price_of_order3)

        self.assertIn("avg_order_item_value", df.columns)
        self.assertEqual(
            avg_order_item_value_today,
            (self.price_of_order1 + self.price_of_order2)
            / (self.order_item_1.quantity + self.order_item_2.quantity),
        )
        self.assertEqual(
            avg_order_item_value_yesterday,
            self.price_of_order3 / self.order_item_3.quantity,
        )

    def test_get_combined_order_item_data_for_staff_user_electronics_category_should_return_data_for_today(
        self,
    ):
        df = DashData.get_combined_order_item_data(
            user=self.staff_user, category=self.category
        )

        (
            total_quantity_order_items_in_day_today,
            total_quantity_order_items_in_day_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )
        (
            total_order_item_payment_today,
            total_order_item_payment_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )
        (
            avg_order_item_value_today,
            avg_order_item_value_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="avg_order_item_value")
        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(
            total_quantity_order_items_in_day_today,
            self.order_item_1.quantity + self.order_item_2.quantity,
        )
        self.assertEqual(total_quantity_order_items_in_day_yesterday, 0)

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(
            total_order_item_payment_today, self.price_of_order1 + self.price_of_order2
        )
        self.assertEqual(total_order_item_payment_yesterday, 0)

        self.assertIn("avg_order_item_value", df.columns)
        self.assertEqual(
            avg_order_item_value_today,
            (self.price_of_order1 + self.price_of_order2)
            / (self.order_item_1.quantity + self.order_item_2.quantity),
        )
        self.assertEqual(avg_order_item_value_yesterday, 0)

    def test_get_combined_order_item_data_for_staff_user_clothes_category_should_return_data_for_yesterday(
        self,
    ):
        df = DashData.get_combined_order_item_data(
            user=self.staff_user, category=self.category2
        )

        (
            total_quantity_order_items_in_day_today,
            total_quantity_order_items_in_day_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_quantity_order_items_in_day"
        )
        (
            total_order_item_payment_today,
            total_order_item_payment_yesterday,
        ) = self.get_data_for_today_and_yesterday(
            df=df, df_name="total_order_item_payment"
        )
        (
            avg_order_item_value_today,
            avg_order_item_value_yesterday,
        ) = self.get_data_for_today_and_yesterday(df=df, df_name="avg_order_item_value")
        self.assertIn("total_quantity_order_items_in_day", df.columns)
        self.assertEqual(total_quantity_order_items_in_day_today, 0)
        self.assertEqual(
            total_quantity_order_items_in_day_yesterday, self.order_item_3.quantity
        )

        self.assertIn("total_order_item_payment", df.columns)
        self.assertEqual(total_order_item_payment_today, 0)
        self.assertEqual(total_order_item_payment_yesterday, self.price_of_order3)

        self.assertIn("avg_order_item_value", df.columns)
        self.assertEqual(avg_order_item_value_today, 0)
        self.assertEqual(
            avg_order_item_value_yesterday,
            self.price_of_order3 / self.order_item_3.quantity,
        )
