from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem
from shop.models import Product

from django.views.generic import ListView

class CartListView(ListView):
    template_name = 'carts/cart_details.html'
    model = CartItem
    context_object_name = 'cart_items'
    ordering = ['-created_at']


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(account=request.user)
    total_price = sum(item.product.unit_price * item.quantity for item in cart_items)
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, 'carts/cart_details.html', context)


@login_required
def add_to_cart(request, product_id, quantity=1):
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product,
                                                        account=request.user)
    if created:
        cart_item.quantity = int(quantity)
        cart_item.save()
        messages.success(request, "Item added to your cart.")
    else:
        if (cart_item.quantity + quantity) <= product.in_stock:
            cart_item.quantity += int(quantity)
            cart_item.save()
            messages.success(request, "Item added to your cart.")
        else:
            messages.warning(request, f"Not enough product in stock. Maximum quantity is {product.in_stock}")
    return redirect('cart:cart_details')


@login_required
def remove_from_cart(request, product_id, quantity=1):
    product = Product.objects.get(id=product_id)
    cart_item = CartItem.objects.get(product=product,
                                     account=request.user)
    cart_item.quantity -= int(quantity)

    if cart_item.quantity <= 0:
        cart_item.delete()
    else:
         cart_item.save()
    messages.success(request, "Item removed from your cart.")
    return redirect('cart:cart_details')


@login_required()
def remove_all(request):
    cart_items = CartItem.objects.filter(account=request.user)
    for item in cart_items:
        item.delete()
        return redirect('cart:cart_details')
