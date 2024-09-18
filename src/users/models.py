from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Account(AbstractUser):
    phone = PhoneNumberField(help_text="User's phone number.")
    birth_date = models.DateField(help_text="User's date of birth.")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
