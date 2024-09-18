from decimal import Decimal

from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

from shop.models import Product
from users.models import Account


class Address(models.Model):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text="User account associated with the address.",
    )
    first_name = models.CharField(
        max_length=50, help_text="First name of the address holder."
    )
    last_name = models.CharField(
        max_length=50, help_text="Last name of the address holder."
    )
    street = models.CharField(max_length=50, help_text="Street name for the shipment.")
    phone = PhoneNumberField(help_text="Phone number associated with the address.")
    city = models.CharField(max_length=50, help_text="City for the shipment.")
    postal_code = models.CharField(
        max_length=6, help_text="Postal code for the shipment."
    )
    state = models.CharField(
        max_length=50, help_text="State or province for the shipment."
    )
    country = models.CharField(max_length=50, help_text="Country for the shipment.")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the address was created."
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"({self.id}) assigned to: {self.account}"


class ShippingType(models.Model):
    type = models.TextField(max_length=50, help_text="Type of shipping.")
    price = models.DecimalField(
        default=0.00,
        decimal_places=2,
        max_digits=100,
        help_text="Cost of this shipping type.",
    )
    # order = models.ForeignKey(OrderItem, on_delete=models.CASCADE)


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        NEW = "NEW", "NEW"
        AWAITING_PAYMENT = "AWAITING_PAYMENT", "AWAITING_PAYMENT"
        UNPAID = "UNPAID", "UNPAID"
        PAID = "PAID", "PAID"

    class OrderShippingStatus(models.TextChoices):
        NEW = "NEW", "NEW"
        IN_PREPARATION = "IN_PREPARATION", "IN_PREPARATION"
        WAITING_FOR_SHIPMENT = "WAITING_FOR_SHIPMENT", "WAITING_FOR_SHIPMENT"
        SHIPPED = "SHIPPED", "SHIPPED"
        DELIVERED = "DELIVERED", "DELIVERED"
        CLOSED = "CLOSED", "CLOSED"

    status = models.TextField(
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        help_text="Current status of the order.",
    )
    shipping_status = models.TextField(
        choices=OrderShippingStatus.choices,
        default=OrderShippingStatus.NEW,
        help_text="Shipping status of the order.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the order was created."
    )
    update_at = models.DateTimeField(
        auto_now=True, help_text="Time when the order was last updated."
    )
    buyer = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        help_text="User account who placed the order.",
    )
    address = models.ForeignKey(
        Address, on_delete=models.PROTECT, help_text="Shipping address for the order."
    )
    shipping_type = models.ForeignKey(
        ShippingType,
        on_delete=models.PROTECT,
        help_text="Selected shipping type for the order.",
    )
    total_price_with_shipping = models.DecimalField(
        default=0.00,
        decimal_places=2,
        max_digits=100,
        help_text="Total price with shipping price of the order including shipping.",
    )

    def get_absolute_url(self):
        return reverse("orders:order-details", args=[str(self.pk)])


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, help_text="Product included in the order."
    )
    quantity = models.PositiveIntegerField(
        default=0, help_text="Quantity of the product ordered."
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text="User account associated with the order item.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the order item was created."
    )
    update_at = models.DateTimeField(
        auto_now=True, help_text="Time when the order item was last updated."
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="order_items",
        help_text="Associated order for the order item.",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_product_cost(self) -> Decimal:
        return self.quantity * self.product.unit_price
