from django.db import models
from django.urls import reverse_lazy
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


class OrderItem(models.Model):
    class OrderStatus(models.TextChoices):
        NEW = "NEW", "NEW"
        PAID = "PAID", "PAID"
        SHIPPED = "SHIPPED", "SHIPPED"
        DELIVERED = "DELIVERED", "DELIVERED"
        CLOSED = "CLOSED", "CLOSED"

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_absolute_url(self):
        return reverse_lazy("carts:cart_details")

    @property
    def total_product_cost(self):
        return self.quantity * self.product.unit_price


class ShippingType(models.Model):
    type = models.TextField(max_length=50)
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
    # order = models.ForeignKey(OrderItem, on_delete=models.CASCADE)


#     class ShippingType(models.TextChoices):
#         COURIER = 'COURIER', 'COURIER'
#         COURIER_CASH_ON_DELIVERY = 'COURIER_CASH_ON_DELIVERY', 'COURIER_CASH_ON_DELIVERY'
#         POST = 'POST', 'POST'
#         PARCEL_LOCKER = 'PARCEL_LOCKER', 'PARCEL_LOCKER'


#
# class Payment(models.Model):
#     class State(models.TextChoices):
#         NEW = 'NEW', 'NEW'
#         PAID = 'PAID', 'PAID'
#
#     paid = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
#     paid_time = models.DateTimeField()
#     state = models.IntegerField(choices=State.choices)
#
