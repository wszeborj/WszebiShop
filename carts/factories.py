import factory
from factory.django import DjangoModelFactory
from faker import Faker

from shop.factories import ProductFactory
from users.factories import AccountFactory

from .models import CartItem

fake = Faker()


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem

    product = factory.SubFactory(ProductFactory)
    quantity = 1
    account = factory.SubFactory(AccountFactory)
    created_at = factory.LazyAttribute(lambda _: fake.past_date())
