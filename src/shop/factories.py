import random
from datetime import timedelta
from io import BytesIO

import factory
from factory.django import DjangoModelFactory
from faker import Faker
from PIL import Image as PilImage

from users.factories import AccountFactory

from .models import Category, Image, Product

fake = Faker()


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("word")
    description = factory.Faker("sentence")


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    category = factory.SubFactory(CategoryFactory)
    unit = random.choice(["piece", "box"])
    unit_price = factory.Faker(
        "pydecimal", left_digits=2, right_digits=2, positive=True
    )
    in_stock = factory.Faker("random_int", min=0, max=1000)
    sold = factory.Faker("random_int", min=0, max=999)
    created_at = factory.LazyAttribute(lambda _: fake.past_date())
    updated_at = factory.LazyAttribute(
        lambda _self: _self.created_at + timedelta(days=365)
    )
    special_offer = factory.Faker("boolean")
    is_active = True
    seller = factory.SubFactory(AccountFactory)


def create_image(width: int = None, height: int = None):
    width = 600 if width is None else width
    height = 800 if height is None else height
    file = BytesIO()
    image = PilImage.new("RGB", (width, height), color=(255, 255, 255))
    image.save(file, "png")
    file.name = factory.Faker("file_name")
    file.seek(0)
    return file


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = Image

    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(width=600, height=800, format="PNG")
    created_at = factory.Faker("date_time_this_year")
