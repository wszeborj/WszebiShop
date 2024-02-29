from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, View

from carts.models import CartItem
from shop.models import Product

from .forms import AddressForm
from .models import Address


class OrderListView(LoginRequiredMixin, ListView):
    template_name = "orders/orders.html"
    model = CartItem
    context_object_name = "cart_items"
    ordering = ["-created_at"]

    def get_queryset(self):
        context = CartItem.objects.filter(account=self.request.user)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_price"] = sum(
            item.product.unit_price * item.quantity for item in context["cart_items"]
        )
        context["shipping_addresses"] = Address.objects.filter(
            account=self.request.user
        )

        return context


class ProductToOrder(LoginRequiredMixin, View):
    def post(self, request, product_id: int):
        product = get_object_or_404(Product, pk=product_id)
        cart_item, created = CartItem.objects.get_or_create(
            product=product, account=request.user
        )
        if created:
            cart_item.quantity = 1
            cart_item.save()
            messages.success(request, "Item added to your order.")
        else:
            if (cart_item.quantity + 1) <= product.in_stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, "Item added to your order.")
                return redirect("orders:order")
            messages.warning(
                request,
                f"Not enough product in stock. Maximum quantity is {product.in_stock}",
            )
        return redirect("orders:order")


class AddAddress(LoginRequiredMixin, FormView):
    template_name = "orders/add-address.html"
    form_class = AddressForm
    success_url = reverse_lazy("orders:order")

    def form_valid(self, form):
        form.instance.account = self.request.user
        form.save()
        messages.success(self.request, "New address added")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Some values in address form were wrong")
        return super().form_invalid(form)
