import pandas as pd
from django.db.models import Count, F, Sum

from orders.models import Order, OrderItem


class DashData:
    @staticmethod
    def get_daily_orders(user=None):
        orders = Order.objects.all()

        if user and not user.is_staff:
            orders = orders.filter(buyer=user)

        orders = (
            orders.values("created_at__date")
            .annotate(order_count=Count("id"))
            .order_by("created_at__date")
        )
        return pd.DataFrame(orders)

    @staticmethod
    def get_daily_total_payments(user=None):
        payments = Order.objects.filter(status=Order.OrderStatus.PAID)

        if user and not user.is_staff:
            payments = payments.filter(buyer=user)

        payments = (
            payments.values("created_at__date")
            .annotate(total_payment=Sum("total_price_with_shipping"))
            .order_by("created_at__date")
        )
        return pd.DataFrame(payments)

    @staticmethod
    def get_daily_order_items(user=None, category=None):
        order_items = OrderItem.objects.all()

        if user and not user.is_staff:
            order_items = order_items.filter(order__buyer=user)

        if category:
            order_items = order_items.filter(product__category=category)

        order_items = (
            order_items.values("created_at__date")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("created_at__date")
        )
        return pd.DataFrame(order_items)

    @staticmethod
    def get_daily_order_items_payments(user=None, category=None):
        payments = Order.objects.filter(status=Order.OrderStatus.PAID)

        if user and not user.is_staff:
            payments = payments.filter(buyer=user)

        if category:
            payments = payments.filter(order_items__product__category=category)

        payments = (
            payments.values("created_at__date")
            .annotate(
                total_order_item_payment=Sum(
                    F("order_items__quantity") * F("order_items__product__unit_price")
                )
            )
            .order_by("created_at__date")
        )
        return pd.DataFrame(payments)

    @staticmethod
    def get_combined_order_data(user=None):
        if user.is_staff:
            user = None

        df_daily_orders = DashData.get_daily_orders(user=user)
        df_daily_payments = DashData.get_daily_total_payments(user=user)
        if not df_daily_orders.empty:
            combined_df = pd.merge(
                df_daily_orders,
                df_daily_payments,
                on="created_at__date",
                how="outer",
            )

            combined_df["avg_order_value"] = (
                combined_df["total_payment"].astype(float) / combined_df["order_count"]
            )

            combined_df = combined_df.fillna(0)
            combined_df.columns = [
                "created_at__date",
                "order_count",
                "total_payment",
                "avg_order_value",
            ]

            return combined_df

        return pd.DataFrame(
            columns=[
                "created_at__date",
                "order_count",
                "total_payment",
                "avg_order_value",
            ]
        )

    @staticmethod
    def get_combined_order_item_data(user=None, category=None):
        if user.is_staff:
            user = None

        df_daily_order_items = DashData.get_daily_order_items(
            user=user, category=category
        )
        df_daily_order_items_payments = DashData.get_daily_order_items_payments(
            user=user, category=category
        )
        if not df_daily_order_items_payments.empty:
            combined_df = pd.merge(
                df_daily_order_items,
                df_daily_order_items_payments,
                on="created_at__date",
                how="outer",
            )
            combined_df["avg_order_item_value"] = (
                combined_df["total_order_item_payment"].astype(float)
                / combined_df["total_quantity"]
            )

            combined_df = combined_df.fillna(0)
            combined_df.columns = [
                "created_at__date",
                "total_quantity",
                "total_order_item_payment",
                "avg_order_item_value",
            ]

            return combined_df

        return pd.DataFrame(
            columns=[
                "created_at__date",
                "total_quantity",
                "total_order_item_payment",
                "avg_order_item_value",
            ]
        )
