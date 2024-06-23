from decimal import Decimal

from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

from shop.models import Product
from users.models import Account


class Address(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    phone = PhoneNumberField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=6)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"({self.id}) assigned to: {self.account}"


class ShippingType(models.Model):
    type = models.TextField(max_length=50)
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
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

    status = models.TextField(choices=OrderStatus.choices, default=OrderStatus.NEW)
    shipping_status = models.TextField(
        choices=OrderShippingStatus.choices, default=OrderShippingStatus.NEW
    )
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    buyer = models.ForeignKey(Account, on_delete=models.PROTECT)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    shipping_type = models.ForeignKey(ShippingType, on_delete=models.PROTECT)
    total_price_with_shipping = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=100
    )
    # seller = models.ForeignKey(Account, on_delete=models.CASCADE)
    # tracking_number = ...

    def get_absolute_url(self):
        return reverse("orders:order-details", args=[str(self.pk)])


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="order_items",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_product_cost(self) -> Decimal:
        return self.quantity * self.product.unit_price
