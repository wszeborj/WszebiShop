from django.db import models

from orders.models import Order
from users.models import Account


class Payment(models.Model):
    class State(models.TextChoices):
        NEW = "NEW", "NEW"
        PAYMENT_FAILURE = "PAYMENT_FAILURE", "PAYMENT_FAILURE"
        PAYMENT_SUCCESS = "PAYMENT_SUCCESS", "PAYMENT_SUCCESS"

    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, help_text="User who made the payment."
    )
    price = models.DecimalField(
        default=0.00,
        decimal_places=2,
        max_digits=100,
        help_text="Total price of the payment.",
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, help_text="Associated order for the payment."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the payment was created."
    )
    state = models.CharField(choices=State.choices, help_text="State of the payment.")
