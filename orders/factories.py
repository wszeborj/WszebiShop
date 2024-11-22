import random
from datetime import timedelta

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from shop.factories import ProductFactory
from users.factories import AccountFactory

from .models import Address, Order, OrderItem, ShippingType

fake = Faker()

POLISH_STATES = [
    "Dolnośląskie",
    "Kujawsko-Pomorskie",
    "Lubelskie",
    "Lubuskie",
    "Łódzkie",
    "Małopolskie",
    "Mazowieckie",
    "Opolskie",
    "Podkarpackie",
    "Podlaskie",
    "Pomorskie",
    "Śląskie",
    "Świętokrzyskie",
    "Warmińsko-Mazurskie",
    "Wielkopolskie",
    "Zachodniopomorskie",
]


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    account = factory.SubFactory(AccountFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    street = factory.Faker("street_name", locale="pl_PL")
    phone = factory.Faker("phone_number", locale="pl_PL")
    city = factory.Faker("city", locale="pl_PL")
    postal_code = factory.Faker("postcode", locale="pl_PL")
    state = random.choice(POLISH_STATES)
    country = "Polska"
    created_at = factory.LazyAttribute(lambda _: fake.past_date())


class ShippingTypeFactory(DjangoModelFactory):
    class Meta:
        model = ShippingType

    type = factory.Faker("word")
    price = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    status = factory.Iterator(Order.OrderStatus.values)
    shipping_status = factory.Iterator(Order.OrderShippingStatus.values)
    created_at = factory.LazyAttribute(lambda _: fake.past_date())
    update_at = factory.LazyAttribute(
        lambda _self: _self.created_at + timedelta(hours=5)
    )
    buyer = factory.SubFactory(AccountFactory)
    address = factory.SubFactory(AddressFactory)
    shipping_type = factory.SubFactory(ShippingTypeFactory)
    total_price_with_shipping = factory.Faker(
        "pydecimal", left_digits=5, right_digits=2, positive=True
    )


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    product = factory.SubFactory(ProductFactory)
    quantity = 1
    account = factory.SubFactory(AccountFactory)
    created_at = factory.LazyAttribute(lambda _: fake.past_date())
    update_at = factory.LazyAttribute(
        lambda _self: _self.created_at + timedelta(hours=5)
    )
    order = factory.SubFactory(OrderFactory)
