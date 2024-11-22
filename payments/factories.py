import factory
from factory.django import DjangoModelFactory
from faker import Faker

from orders.factories import OrderFactory
from users.factories import AccountFactory

from .models import Payment

fake = Faker()


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    user = factory.SubFactory(AccountFactory)
    order = factory.SubFactory(OrderFactory)
    price = factory.SelfAttribute("order.total_price_with_shipping")
    created_at = factory.LazyAttribute(lambda _: fake.past_date())
    state = factory.Iterator(Payment.State.values)
