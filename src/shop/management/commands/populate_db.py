import os
import random
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from faker import Faker

from core.settings import MEDIA_ROOT
from orders.models import ShippingType
from shop.models import Category, Image, Product


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
        admin_password = os.environ.get("DJANGO_ADMIN_PASSWORD")

        if not admin_password:
            self.style.write(
                self.style.ERROR("DJANGO_ADMIN_PASSWORD env variable not set")
            )

        user = User.objects.create_superuser(
            username="admin",
            email="admin@admin.com",
            password=admin_password,
            phone="123456789",
            birth_date=datetime.fromisoformat("1990-12-04"),
            status="ACTIVE",
        )
        self.stdout.write(
            self.style.SUCCESS(f'Superuser "{user} created successfully.')
        )

    def create_batch_categories(self):
        categories = [
            "Elektronika",
            "Odzież",
            "Książki",
            "Komputery",
            "Sport",
            "Motoryzacja",
        ]
        for category_name in categories:
            Category.objects.create(name=category_name)

        self.stdout.write(self.style.SUCCESS("Categories created successfully."))

    def create_batch_products(self):
        fake = Faker()
        for _ in range(10):
            name = fake.catch_phrase()
            description = fake.text()
            category = random.choice(Category.objects.all())
            unit = random.choice(["szt"])
            unit_price = round(random.uniform(1.00, 10000.00), 2)
            in_stock = random.randint(1, 10)
            sold = random.randint(0, in_stock)
            special_offer = random.choice([True, False])

            product = Product.objects.create(
                name=name,
                description=description,
                category=category,
                unit=unit,
                unit_price=unit_price,
                in_stock=in_stock,
                sold=sold,
                special_offer=special_offer,
            )

            product.save()

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
        folder_path = os.path.join(MEDIA_ROOT, "product_images/")
        for product in Product.objects.all():
            num_images = random.randint(0, 3)
            selected_images = self.generate_random_images(
                folder_path=folder_path, num_images=num_images
            )

            for image_file in selected_images:
                image_path = os.path.join(folder_path, image_file)
                with open(image_path, "rb") as f:
                    image_obj = Image.objects.create(product=product)
                    image_obj.image.save(image_file, File(f))
                    image_obj.save()

    def create_batch_shipping_type(self):
        types = ["courier", "courier_cash_on_delivery", "post", "parcel_locker"]
        for type in types:
            ShippingType.objects.create(
                type=type, price=round(random.uniform(5.00, 100.00), 2)
            )
        self.stdout.write(self.style.SUCCESS("Shipping types created successfully."))

        # product1 = Product.objects.create(
        #     name='Aparat1',
        #     description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. In vel enim sed velit lobortis'
        #                 ' ullamcorper non nec sem. Nunc varius tortor leo. Curabitur eget elit interdum, tempor'
        #                 ' ex non, vehicula nulla. Phasellus in venenatis nunc. Nullam vitae leo nunc. Nullam in'
        #                 ' pretium mauris. Cras volutpat nibh et nulla fermentum feugiat. Proin quis placerat ipsum.'
        #                 ' Cras placerat sagittis quam, ac ultricies ex faucibus quis. Ut quis nulla et dolor maximus'
        #                 ' tempus. Cras elementum, ante nec pretium ullamcorper, risus arcu rhoncus odio, ut'
        #                 ' pellentesque nisi sapien vel nibh. Suspendisse pulvinar lacinia arcu at vestibulum.',
        #     category=1,
        #     unit="szt",
        #     unit_price=111.11,
        #     quantity_in_stock=5,
        #     sold=3,
        #     special_offer=False,
        #     is_active=True)
