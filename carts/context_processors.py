from django.db.models import Sum

from .models import CartItem


def cart_items_count_processor(request) -> dict[str, any]:
    context = {"cart_total_quantity": 0}
    if request.user.is_anonymous:
        return context

    cart_items_quantity = CartItem.objects.filter(account=request.user).aggregate(
        total=Sum("quantity")
    )["total"]

    if cart_items_quantity is not None:
        context["cart_total_quantity"] = cart_items_quantity

    return context
