from django.db import models
from django.urls import reverse_lazy
from shop.models import Product
from users.models import Account


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_absolute_url(self):
        return reverse_lazy("carts:cart_details")

    @property
    def total_product_cost(self):
        return self.quantity * self.product.unit_price

