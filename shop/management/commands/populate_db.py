import os
import random
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker

from core.env import env
from core.settings import MEDIA_ROOT
from orders.models import ShippingType
from shop.models import Category, Image, Product
from users.models import Account


class Command(BaseCommand):
    help = "Create a superuser with custom options"

    def handle(self, *args, **options):
        self.create_super_user()
        self.create_batch_categories()
        self.create_batch_products()
        self.create_batch_images()
        self.create_batch_shipping_type()

    def create_super_user(self):
        User = get_user_model()
        if not User.objects.filter(username=env("SUPERUSER_NAME")).exists():
            user = User.objects.create_superuser(
                username=env("SUPERUSER_NAME"),
                email=env("SUPERUSER_MAIL"),
                password=env("SUPERUSER_PASSWORD"),
                phone="123456789",
                birth_date=datetime.fromisoformat("1990-12-04"),
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{user} created successfully.')
            )
        else:
            self.stdout.write(self.style.SUCCESS("Superuser already exist."))

    def create_batch_categories(self):
        if not Category.objects.exists():
            categories = [
                "Electronics",
                "Clothing",
                "Books",
                "Computers",
                "Sports",
                "Automotive",
            ]
            for category_name in categories:
                Category.objects.bulk_create([Category(name=category_name)])

            self.stdout.write(self.style.SUCCESS("Categories created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS("Categories already created."))

    def create_batch_products(self):
        fake = Faker()
        products = []
        for _ in range(10):
            name = fake.name()[:50]
            description = fake.text()[:255]
            category = random.choice(Category.objects.all())
            unit = random.choice(["piece"])
            unit_price = round(random.uniform(1.00, 10000.00), 2)
            in_stock = random.randint(1, 10)
            sold = random.randint(0, in_stock - 1)
            special_offer = False
            seller = random.choice(Account.objects.all())

            products.append(
                Product(
                    name=name,
                    description=description,
                    category=category,
                    unit=unit,
                    unit_price=unit_price,
                    in_stock=in_stock,
                    sold=sold,
                    special_offer=special_offer,
                    seller=seller,
                )
            )

        Product.objects.bulk_create(products)

        self.stdout.write(self.style.SUCCESS("Products created successfully."))

    def generate_random_images(self, folder_path: str, num_images: int):
        ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

        if not os.path.exists(folder_path):
            print(f"Folder path '{folder_path}' does not exist.")
            return []

        images = []
        for file in os.listdir(folder_path):
            if os.path.splitext(file)[1].lower() in ALLOWED_IMAGE_EXTENSIONS:
                images.append(file)

        selected_images = random.sample(images, num_images)

        return selected_images

    def create_batch_images(self):
        folder_path = os.path.join(MEDIA_ROOT, "product_images_examples/")
        products = Product.objects.all()
        for product in products:
            num_images = random.randint(0, 3)
            selected_images = self.generate_random_images(
                folder_path=folder_path, num_images=num_images
            )

            for image_file in selected_images:
                clean_name = (
                    slugify(os.path.splitext(image_file)[0])
                    + os.path.splitext(image_file)[1]
                )
                image_path = os.path.join(folder_path, image_file)
                with open(image_path, "rb") as f:
                    django_file = File(f)
                    image_obj = Image(product=product)
                    image_obj.image.save(clean_name, django_file, save=False)
                    image_obj.save()
        self.stdout.write(self.style.SUCCESS("Pictures created successfully."))

    def create_batch_shipping_type(self):
        if not ShippingType.objects.exists():
            shipping_types = [
                "courier",
                "courier_cash_on_delivery",
                "post",
                "parcel_locker",
            ]

            ShippingType.objects.bulk_create(
                [
                    ShippingType(
                        type=shipping_type, price=round(random.uniform(5.00, 100.00), 2)
                    )
                    for shipping_type in shipping_types
                ]
            )

            self.stdout.write(
                self.style.SUCCESS("Shipping types created successfully.")
            )
        else:
            self.stdout.write(self.style.SUCCESS("Shipping types already created."))
