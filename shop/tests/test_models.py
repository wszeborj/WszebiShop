from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from ..factories import CategoryFactory, ImageFactory, ProductFactory, create_image


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = CategoryFactory(name="Test Category")

    def test_str(self):
        self.assertEqual(str(self.category), "Test Category")

    def test_get_absolute_url(self):
        base_url = reverse("shop:category-filtered-products")
        expected_url = f"{base_url}?category={self.category.pk}"
        self.assertEqual(self.category.get_absolute_url(), expected_url)


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = ProductFactory(name="Test Product")

    def test_str(self):
        self.assertEqual(str(self.product), f"Test Product ({self.product.pk})")

    def test_get_absolute_url(self):
        expected_url = reverse("shop:product-details", args=[str(self.product.pk)])
        self.assertEqual(self.product.get_absolute_url(), expected_url)

    def test_first_image(self):
        self.assertIsNone(self.product.first_image())

    def test_get_thumbnail(self):
        self.assertIsNone(self.product.get_thumbnail())


class ImageModelTest(TestCase):
    def setUp(self):
        self.product = ProductFactory(name="Test Product")
        image = create_image()
        image_file = SimpleUploadedFile(
            name="test.png", content=image.read(), content_type="image/png"
        )
        self.image = ImageFactory(product=self.product, image=image_file)

    def test_str(self):
        expected_output = f"Image ({self.image.id}) {self.image.image.name} for product ({self.product.id}) {self.product.name}."
        self.assertEqual(str(self.image), expected_output)

    def test_save_thumbnail(self):
        self.assertTrue(self.image.thumbnail)
        self.assertEqual(self.image.image.height, 500)
        self.assertEqual(self.image.image.width, 333)
