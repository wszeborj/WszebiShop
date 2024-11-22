import factory
from factory.django import DjangoModelFactory
from phonenumber_field.phonenumber import PhoneNumber

from .models import Account


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Account

    username = factory.Sequence(lambda n: f"user_{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    email = factory.LazyAttribute(
        lambda obj: f"{obj.first_name}.{obj.last_name}@example.com".lower()
    )
    phone = factory.LazyFunction(lambda: PhoneNumber.from_string("+48123456789"))
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")
    birth_date = factory.Faker("date_of_birth")
    is_active = True
