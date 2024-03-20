from django.db import models

from orders.models import Order
from users.models import Account


class Payment(models.Model):
    class State(models.TextChoices):
        NEW = "NEW", "NEW"
        PAID = "PAID", "PAID"

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(choices=State.choices)
