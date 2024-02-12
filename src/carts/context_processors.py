from .models import CartItem



def cart_items_count_processor(request):
    cart_items = CartItem.objects.filter(account=request.user)
    cart_total_quantity = 0
    for item in cart_items:
        cart_total_quantity += item.quantity
    context = {'cart_total_quantity': cart_total_quantity}

    return context