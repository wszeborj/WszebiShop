from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View

from shop.models import Product

from .forms import CartUpdateForm
from .models import CartItem


class CartListView(LoginRequiredMixin, ListView):
    template_name = "carts/cart_details.html"
    model = CartItem
    context_object_name = "cart_items"
    ordering = ["-created_at"]

    def get_queryset(self):
        return CartItem.objects.filter(account=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ProductsProcessing.check_products_availability(request=self.request)

        context["total_price"] = sum(
            item.product.unit_price * item.quantity for item in context["cart_items"]
        )

        update_quantity_form = CartUpdateForm()
        context["update_quantity_form"] = update_quantity_form

        sellers = set(item.product.seller for item in context["cart_items"])
        context["one_seller"] = len(sellers) == 1
        if not context["one_seller"]:
            messages.warning(
                self.request,
                "To proceed to order you can have only products from the same seller.",
            )

        return context


class AddToCart(LoginRequiredMixin, View):
    redirect_field_name = None

    def post(self, request, product_id: int, quantity: int = 1):
        product = get_object_or_404(Product, pk=product_id)
        cart_item, created = CartItem.objects.get_or_create(
            product=product, account=request.user
        )
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
                messages.warning(
                    request,
                    f"Not enough product in stock. Maximum quantity is {product.in_stock}",
                )
        return redirect("carts:cart-details")


class RemoveFromCart(LoginRequiredMixin, View):
    def post(self, request, product_id, quantity=1):
        product = get_object_or_404(Product, pk=product_id)
        cart_item = CartItem.objects.get(product=product, account=request.user)
        cart_item.quantity -= int(quantity)

        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
        messages.success(request, "Item removed from your cart.")
        return redirect("carts:cart-details")


class RemoveAll(LoginRequiredMixin, View):
    def post(self, request):
        cart_items = CartItem.objects.filter(account=request.user)
        for item in cart_items:
            item.delete()

        messages.success(request, "All items removed from your cart.")

        return redirect("carts:cart-details")


class RemoveItem(LoginRequiredMixin, View):
    def post(self, request, cart_item_id):
        cart_item = get_object_or_404(CartItem, pk=cart_item_id)
        cart_item.delete()
        messages.success(request, "Item removed from your cart.")

        return redirect("carts:cart-details")


class UpdateCart(LoginRequiredMixin, View):
    def post(self, request, product_id):
        cart_item = get_object_or_404(
            CartItem, product_id=product_id, account=request.user
        )
        form = CartUpdateForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            product = cart_item.product
            if quantity > product.in_stock:
                messages.warning(request, f"Only {product.in_stock} items available")
            else:
                cart_item.quantity = int(quantity)
                if cart_item.quantity == 0:
                    cart_item.delete()
                    messages.success(request, "Quantity updated. Item removed")
                else:
                    cart_item.save()
                    messages.success(request, "Quantity updated.")
        return redirect("carts:cart-details")


class ProductsProcessing:
    @staticmethod
    def check_products_availability(request, redirect_page=False):
        cart_items = CartItem.objects.filter(account=request.user)
        for item in cart_items:
            if item.product.in_stock < item.quantity:
                if redirect_page:
                    return redirect("carts:cart-details")

                messages.warning(
                    request,
                    f"The product {item.product.name} is not available in the requested quantity of {item.quantity}. "
                    f"Available quantity: {item.product.in_stock}",
                )
                item.quantity = item.product.in_stock
                item.save()
