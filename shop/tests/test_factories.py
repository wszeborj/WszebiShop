from django.test import TestCase

from users.models import Account

from ..factories import CategoryFactory, ImageFactory, ProductFactory
from ..models import Category, Image, Product

# from icecream import ic


class CategoryFactoryTest(TestCase):
    def test_create_single_object(self):
        category = CategoryFactory.create()
        # ic(category)
        # ic_all_attributes(category)

        self.assertIsInstance(category, Category)
        self.assertEqual(Category.objects.count(), 1)
        self.assertIsNotNone(category.name)
        self.assertIsNotNone(category.description)

    def test_create_multiple_objects(self):
        CategoryFactory.create_batch(10)

        self.assertEqual(Category.objects.count(), 10)


class ProductFactoryTest(TestCase):
    def test_create_single_object(self):
        product = ProductFactory.create()
        # ic(product)
        # ic_all_attributes(product)

        self.assertIsInstance(product, Product)
        self.assertEqual(Product.objects.count(), 1)
        self.assertIsNotNone(product.name)
        self.assertIsNotNone(product.description)
        self.assertIsNotNone(product.category)
        self.assertIsInstance(product.category, Category)
        self.assertEqual(Category.objects.count(), 1)
        self.assertIsNotNone(product.unit)
        self.assertGreater(product.unit_price, 0.00)
        self.assertGreaterEqual(product.in_stock, 0)
        self.assertGreaterEqual(product.sold, 0)
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)
        self.assertIsNotNone(product.special_offer)
        self.assertTrue(product.is_active)
        self.assertIsNotNone(product.seller)
        self.assertIsInstance(product.seller, Account)
        self.assertEqual(Account.objects.count(), 1)

    def test_create_multiple_objects(self):
        ProductFactory.create_batch(10)
        self.assertEqual(Product.objects.count(), 10)


class ImageFactoryTest(TestCase):
    def test_create_single_object(self):
        image = ImageFactory.create()
        # ic(image)
        # ic_all_attributes(image)

        self.assertIsInstance(image, Image)
        self.assertEqual(Image.objects.count(), 1)
        self.assertIsNotNone(image.product)
        self.assertIsInstance(image.product, Product)
        self.assertEqual(Product.objects.count(), 1)
        self.assertIsNotNone(image.image)
        self.assertIsNotNone(image.created_at)

    def test_create_multiple_objects(self):
        ImageFactory.create_batch(10)
        self.assertEqual(Image.objects.count(), 10)
