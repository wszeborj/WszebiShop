import django_filters
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, View
from django_filters.views import FilterView

from carts.models import CartItem
from carts.views import ProductsProcessing
from shop.models import Product

from .forms import AddressForm
from .models import Address, Order, ShippingType
from .utils import clean_empty_orders


class OrderConfirmationListView(LoginRequiredMixin, ListView):
    template_name = "orders/orders_confirmation.html"
    model = CartItem
    context_object_name = "cart_items"
    ordering = ["-created_at"]

    def get_queryset(self):
        context = CartItem.objects.filter(account=self.request.user)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ProductsProcessing.check_products_availability(request=self.request)

        total_price = sum(
            item.product.unit_price * item.quantity for item in context["cart_items"]
        )
        shipping_addresses = Address.objects.filter(account=self.request.user)

        context["total_price"] = total_price
        context["shipping_addresses"] = shipping_addresses
        context["shipping_types"] = ShippingType.objects.all()

        if shipping_addresses:
            selected_shipping_address_id = self.request.GET.get("shipping_address")
            if selected_shipping_address_id:
                address = Address.objects.get(id=selected_shipping_address_id)
            else:
                address = shipping_addresses.latest("created_at")
        else:
            messages.warning(self.request, "To proceed please add shipping address!")
            address = None

        selected_shipping_type_id = self.request.GET.get("shipping_type")
        if selected_shipping_type_id:
            shipping_type = ShippingType.objects.get(id=selected_shipping_type_id)
        else:
            shipping_type = ShippingType.objects.last()

        total_price_with_shipping = total_price + shipping_type.price

        context["selected_shipping_type"] = shipping_type
        context["selected_shipping_address"] = address
        context["total_price_with_shipping"] = total_price_with_shipping

        context["one_seller"] = True
        sellers = set(item.product.seller for item in context["cart_items"])
        if len(sellers) > 1:
            messages.warning(
                self.request,
                "You can only place an order with products from the same seller.",
            )
            context["one_seller"] = False

        return context


class ProductToOrder(LoginRequiredMixin, View):
    def post(self, request, product_id: int):
        product = get_object_or_404(Product, pk=product_id)
        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            account=request.user,
            defaults={"product": product, "account": request.user, "quantity": 1},
        )
        if created:
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
        return redirect("orders:order-confirmation")


class AddAddress(LoginRequiredMixin, FormView):
    template_name = "orders/add-address.html"
    form_class = AddressForm
    success_url = reverse_lazy("orders:order-confirmation")

    def form_valid(self, form):
        form.instance.account = self.request.user
        form.save()
        messages.success(self.request, "New address added")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Some values in address form were wrong")
        return super().form_invalid(form)


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            "status": ["exact"],
        }


class OrderListView(LoginRequiredMixin, FilterView):
    template_name = "orders/orders_list.html"
    model = Order
    context_object_name = "order_items"
    ordering = ["-created_at"]
    filterset_class = OrderFilter

    def get_queryset(self) -> QuerySet[Order]:
        clean_empty_orders()
        return super().get_queryset().filter(buyer=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return super().get_queryset().filter(buyer=self.request.user)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # order_items = OrderItem.objects.filter(order=self.object)
    #     # context["order_items"] = order_items
    #     return context


class SalesFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            "status": ["exact"],
        }


class SalesListView(LoginRequiredMixin, FilterView):
    template_name = "orders/orders_list.html"
    model = Order
    context_object_name = "order_items"
    ordering = ["-created_at"]
    filterset_class = SalesFilter

    def get_queryset(self) -> QuerySet[Order]:
        return super().get_queryset().filter(buyer=self.request.user)
