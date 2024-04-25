from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Account(AbstractUser):
    class State(models.TextChoices):
        NEW = "NEW", "NEW"
        ACTIVE = "ACTIVE", "ACTIVE"
        BLOCKED = "BLOCKED", "BLOCKED"
        BANNED = "BANNED", "BANNED"
        REMOVED = "REMOVED", "REMOVED"

    class Mode(models.TextChoices):
        SELLER = "SELLER", "SELLER"
        BUYER = "BUYER", "BUYER"

    phone = PhoneNumberField()
    birth_date = models.DateField()
    status = models.TextField(choices=State.choices, default=State.NEW)
    mode = models.TextField(choices=Mode.choices, default=Mode.BUYER)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
