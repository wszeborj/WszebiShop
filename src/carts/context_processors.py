from .models import CartItem
from django.db.models import Sum



def cart_items_count_processor(request):
    # cart_items = CartItem.objects.filter(account=request.user)
    # cart_total_quantity = 0
    # for item in cart_items:
    #     cart_total_quantity += item.quantity
    # context = {'cart_total_quantity': cart_total_quantity}
    context = {'cart_total_quantity': 0}
    cart_items_quantity = CartItem.objects.filter(account=request.user).aggregate(total=Sum('quantity'))['total']

    if cart_items_quantity is not None:
        context['cart_total_quantity'] = cart_items_quantity

    return context