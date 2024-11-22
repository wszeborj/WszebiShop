import pandas as pd
from django.db.models import Count, Sum

from orders.models import Order, OrderItem


class DashData:
    @staticmethod
    def get_daily_orders():
        orders = (
            Order.objects.values("created_at__date")
            .annotate(order_count=Count("id"))
            .order_by("created_at__date")
        )
        return pd.DataFrame(orders)

    @staticmethod
    def get_daily_order_items():
        order_items = (
            OrderItem.objects.values("created_at__date")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("created_at__date")
        )
        return pd.DataFrame(order_items)

    @staticmethod
    def get_daily_payments():
        payments = (
            Order.objects.values("created_at__date")
            .annotate(total_payment=Sum("total_price_with_shipping"))
            .order_by("created_at__date")
        )
        return pd.DataFrame(payments)

    @staticmethod
    def get_combined_data_by_date():
        df_daily_orders = DashData.get_daily_order_items()
        df_daily_order_items = DashData.get_daily_order_items()
        df_daily_payments = DashData.get_daily_payments()
        if OrderItem.objects.count() > 0:
            combined_df = pd.merge(
                df_daily_orders,
                df_daily_order_items,
                on="created_at__date",
                how="outer",
            )
            combined_df = pd.merge(
                combined_df, df_daily_payments, on="created_at__date", how="outer"
            )

            combined_df = combined_df.fillna(0)
            combined_df.columns = [
                "created_at__date",
                "order_count",
                "total_quantity",
                "total_payment",
            ]

            return combined_df

        return pd.DataFrame(
            columns=[
                "created_at__date",
                "order_count",
                "total_quantity",
                "total_payment",
            ]
        )
