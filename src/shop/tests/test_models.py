from django.test import TestCase
from shop.models import Category, Product


class TestCategoriesModel(TestCase):

    def setUp(self):
        self.data1 = Category.objects.create(name='django', parent=None)

    def test_category_model_entry(self):
        data = self.data1
        self.assertTrue(isinstance(data, Category))

    def test_category_model_return(self):
        data = self.data1
        self.assertEqual(str(data), 'django')


class TestProductModel(TestCase):

    def setUp(self):
        Category.objects.create(
            name='django_category',
            parent=None)
        self.data1 = Product.objects.create(
            name='django_product',
            description='',
            category_id=1,
            unit='szt',
            unit_price=1.00,
            quantity_in_stock=10,
            sold=0,
            special_offer=False)

    def test_product_model_entry(self):
        data = self.data1
        self.assertTrue(isinstance(data, Product))

    def test_product_model_return(self):
        data = self.data1
        self.assertEqual(str(data), 'django_product (1)')
