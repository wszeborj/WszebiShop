from .models import Order


def clean_empty_orders():
    empty_orders = Order.objects.filter(order_items__isnull=True)
    empty_orders.delete()
