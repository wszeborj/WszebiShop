from django.shortcuts import redirect
from django.contrib import messages
from .models import CartItem
from shop.models import Product
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin


class CartListView(LoginRequiredMixin, ListView):
    template_name = 'carts/cart_details.html'
    model = CartItem
    context_object_name = 'cart_items'
    ordering = ['-created_at']

    def get_queryset(self):
        return CartItem.objects.filter(account=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = sum(item.product.unit_price * item.quantity for item in context['cart_items'])
        return context


class AddToCart(LoginRequiredMixin, View):
    def post(self, request, product_id: int, quantity: int = 1):
        product = get_object_or_404(Product, pk=product_id)
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
        return redirect('carts:cart-details')


class RemoveFromCart(LoginRequiredMixin, View):
    def post(self, request, product_id, quantity=1):
        product = get_object_or_404(Product, pk=product_id)
        cart_item = CartItem.objects.get(product=product,
                                         account=request.user)
        cart_item.quantity -= int(quantity)

        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
        messages.success(request, "Item removed from your cart.")
        return redirect('carts:cart-details')


class RemoveAll(LoginRequiredMixin, View):
    def post(self, request):
        cart_items = CartItem.objects.filter(account=request.user)
        for item in cart_items:
            item.delete()

        return redirect('carts:cart-details')
