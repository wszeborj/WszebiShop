from django.db import models
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
        SHIPPED = "SHIPPED", "SHIPPED"
        DELIVERED = "DELIVERED", "DELIVERED"
        CLOSED = "CLOSED", "CLOSED"

    status = models.TextField(choices=OrderStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    buyer = models.ForeignKey(Account, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    shipping_type = models.ForeignKey(ShippingType, on_delete=models.CASCADE)
    total_price_with_shipping = models.DecimalField(
        default=0.00, decimal_places=2, max_digits=100
    )
    # tracking_number = ...


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_product_cost(self):
        return self.quantity * self.product.unit_price
