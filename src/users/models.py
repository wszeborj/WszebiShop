from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    class State(models.TextChoices):
        NEW = 'NEW', 'NEW'
        ACTIVE = 'ACTIVE', 'ACTIVE'
        BLOCKED = 'BLOCKED', 'BLOCKED'
        BANNED = 'BANNED', 'BANNED'
        REMOVED = 'REMOVED', 'REMOVED'
    phone = PhoneNumberField()
    birth_date = models.DateField()
    status = models.TextField(choices=State.choices)
