from django.test import TestCase, tag
from icecream import ic

from ..factories import CategoryFactory, ImageFactory, ProductFactory
from ..models import Category, Image, Product


class CategoryFactoryTest(TestCase):
    # @tag('x')
    def test_create_single_object(self):
        category = CategoryFactory.create()
        ic(category)

        self.assertIsInstance(category, Category)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_multiple_objects(self):
        category = CategoryFactory.create_batch(10)
        ic(category)
        self.assertEqual(Category.objects.count(), 10)


class ProductFactoryTest(TestCase):
    # @tag('x')
    def test_create_single_object(self):
        product = ProductFactory.create()
        ic(product)

        self.assertIsInstance(product, Product)
        self.assertEqual(Product.objects.count(), 1)
        self.assertIsNotNone(product.name)
        self.assertIsNotNone(product.description)
        self.assertIsNotNone(product.category)
        self.assertIsNotNone(product.unit)
        self.assertGreater(product.unit_price, 0.00)
        self.assertGreaterEqual(product.in_stock, 0)
        self.assertGreaterEqual(product.sold, 0)
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)
        self.assertIsNotNone(product.special_offer)
        self.assertTrue(product.is_active)
        self.assertIsNotNone(product.seller)

    def test_create_multiple_objects(self):
        product = ProductFactory.create_batch(10)
        ic(product)
        self.assertEqual(Product.objects.count(), 10)


class ImageFactoryTest(TestCase):
    # @tag('x')
    def test_create_single_object(self):
        image = ImageFactory.create()
        ic(image)
        ic(image.thumbnail)

        self.assertIsInstance(image, Image)
        self.assertEqual(Image.objects.count(), 1)
        self.assertIsNotNone(image.product.name)
        self.assertIsNotNone(image.image)
        self.assertIsNotNone(image.created_at)

    def test_create_multiple_objects(self):
        image = ImageFactory.create_batch(10)
        ic(image)
        self.assertEqual(Image.objects.count(), 10)
