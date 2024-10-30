from decimal import Decimal

from django.db import models
from django.urls import reverse_lazy

from shop.models import Product
from users.models import Account


class CartItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text="Product associated with the cart item.",
    )
    quantity = models.PositiveIntegerField(
        default=0, help_text="Quantity of the product in the cart."
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        help_text="User account owning this cart item.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the cart item was created."
    )

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    def get_absolute_url(self) -> str:
        return reverse_lazy("carts:cart-details")

    @property
    def total_product_cost(self) -> Decimal:
        return self.quantity * self.product.unit_price
