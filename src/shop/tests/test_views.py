from http import HTTPStatus
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase, tag
from icecream import ic
from PIL import Image as PilImage

from shop.models import Category, Image, Product
from users.models import Account


class TestShopViews(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.account = self.user_model.objects.create_user(
            username="test_user",
            first_name="test_name",
            last_name="test_last_name",
            email="test@test.com",
            password="Test.Password",
            phone="1234567890",
            birth_date="1990-12-04",
            is_active=True,
        )
        self.category = Category.objects.create(
            name="test_category",
        )

        self.product = Product.objects.create(
            name="test_product",
            description="test_description",
            category=self.category,
            unit="test_unit",
            unit_price=100.00,
            in_stock=100,
            sold=0,
            is_active=True,
            seller=self.account,
        )

        self.client.login(username="test_user", password="Test.Password")
        # self.client.force_login(self.account)

        # urls
        self.all_product_list_url = reverse("shop:all-product-list")
        self.product_detail_url = reverse(
            "shop:product-details", args=[self.product.id]
        )
        self.product_create_url = reverse("shop:product-create")
        self.product_update_url = reverse("shop:product-update", args=[self.product.id])
        self.product_delete_url = reverse("shop:product-delete", args=[self.product.id])
        self.product_category_filtered_url = reverse("shop:category-filtered-products")
        self.search_result_url = reverse("shop:search-results")

    def _create_image(self, width, height):
        file = BytesIO()
        image = PilImage.new("RGB", (width, height), color=(255, 255, 255))
        image.save(file, "png")
        file.name = "test.png"
        file.seek(0)
        return file

    def test_all_product_list_GET(self):
        response = self.client.get(self.all_product_list_url)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/home.html")

    def test_product_details_GET(self):
        response = self.client.get(self.product_detail_url)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/product-details.html")

    # @tag('x')
    def test_product_create_POST_no_image(self):
        response = self.client.post(
            self.product_create_url,
            {
                "name": "test_product2",
                "description": "test_description2",
                "category": self.category.id,
                "unit": "test_unit",
                "unit_price": 200.00,
                "in_stock": 200,
                "sold": 0,
                "is_active": True,
            },
        )

        ic()
        ic(vars(response))
        ic(Product.objects.all())

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEquals(Product.objects.count(), 2)
        # check first element because ordering of products is "-created_at"
        self.assertEquals(Product.objects.first().name, "test_product2")

    # @tag('x')
    def test_product_create_POST_no_data_should_not_create_new_object(self):
        self.assertEquals(Product.objects.count(), 1)

        response = self.client.post(self.product_create_url)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)

    # @tag('x')
    def test_product_create_POST_with_valid_image(self):
        # usuwanie produktów
        # valid image (334x501)
        image = SimpleUploadedFile(
            name="valid_test_image.png",
            content=self._create_image(334, 501).read(),
            content_type="image/png",
        )

        response = self.client.post(
            self.product_create_url,
            data={
                "name": "test_product2",
                "description": "test_product2",
                "category": self.category.id,
                "unit": "test_unit",
                "unit_price": 200.00,
                "in_stock": 200,
                "sold": 0,
                "is_active": True,
                "image": [image],
            },
            format="multipart/form-data",
        )
        ic()
        ic(vars(response))
        ic(Product.objects.all())

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEquals(Product.objects.count(), 2)
        # check first element because ordering of products is "-created_at"
        self.assertEquals(Product.objects.first().name, "test_product2")
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(Image.objects.first().product, self.product)

    # @tag('x')
    def test_product_create_POST_invalid_image_should_not_create_new_object(self):
        # valid image (333x500)
        image = SimpleUploadedFile(
            name="valid_test_image.png",
            content=self._create_image(50, 100).read(),
            content_type="image/jpeg",
        )

        new_product_data = {
            "name": "test_product2",
            "description": "test_product2",
            "category": self.category.id,
            "unit": "test_unit",
            "unit_price": 200.00,
            "in_stock": 200,
            "sold": 0,
            "is_active": True,
            "image": image,
        }

        response = self.client.post(self.product_create_url, data=new_product_data)

        ic()
        ic(Product.objects.all())
        ic(Image.objects.all())

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)

    # @tag('x')
    def test_product_update_POST_no_image(self):
        updated_product_data = {
            "name": "updated_product",
            "description": "updated_test_description",
            "category": self.category.id,
            "unit": "updated_unit",
            "unit_price": 300.00,
            "in_stock": 300,
            "sold": 1,
            "is_active": False,
        }

        response = self.client.post(
            path=self.product_update_url, data=updated_product_data, follow=True
        )
        self.product.refresh_from_db()

        self.assertTemplateUsed(response, "shop/product-update.html")
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)
        self.assertEquals(self.product.name, updated_product_data["name"])
        self.assertEquals(self.product.description, updated_product_data["description"])
        self.assertEquals(self.product.unit, updated_product_data["unit"])
        self.assertEquals(self.product.unit_price, updated_product_data["unit_price"])
        self.assertEquals(self.product.in_stock, updated_product_data["in_stock"])
        self.assertEquals(self.product.sold, updated_product_data["sold"])
        self.assertEquals(self.product.is_active, updated_product_data["is_active"])

    # @tag('x')
    def test_product_update_POST_with_valid_image(self):
        # valid image (334x501)
        image = SimpleUploadedFile(
            name="updated_test_image.png",
            content=self._create_image(334, 501).read(),
            content_type="image/jpeg",
        )

        updated_product_data = {
            "name": "updated_product",
            "description": "updated_test_description",
            "category": self.category.id,
            "unit": "updated_unit",
            "unit_price": 300.00,
            "in_stock": 300,
            "sold": 1,
            "is_active": False,
            "image": image,
        }

        response = self.client.post(
            path=self.product_update_url, data=updated_product_data, follow=True
        )

        ic()
        ic(vars(response))
        ic(Product.objects.all())

        self.assertTemplateUsed(response, "shop/product-update.html")
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)
        self.assertEquals(self.product.name, updated_product_data["name"])
        self.assertEquals(self.product.description, updated_product_data["description"])
        self.assertEquals(self.product.unit, updated_product_data["unit"])
        self.assertEquals(self.product.unit_price, updated_product_data["unit_price"])
        self.assertEquals(self.product.in_stock, updated_product_data["in_stock"])
        self.assertEquals(self.product.sold, updated_product_data["sold"])
        self.assertEquals(self.product.is_active, updated_product_data["is_active"])
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(Image.objects.first().product, self.product)

    # @tag('x')
    def test_product_update_POST_invalid_image_should_not_update_product(self):
        # valid image (333x500)
        image = SimpleUploadedFile(
            name="valid_test_image.png",
            content=self._create_image(50, 100).read(),
            content_type="image/jpeg",
        )

        updated_product_data = {
            "name": "updated_product",
            "description": "updated_test_description",
            "category": self.category.id,
            "unit": "updated_unit",
            "unit_price": 300.00,
            "in_stock": 300,
            "sold": 1,
            "is_active": False,
            "image": image,
        }

        response = self.client.post(
            path=self.product_update_url, data=updated_product_data, follow=True
        )

        ic()
        ic(Product.objects.all())
        ic(Image.objects.all())

        self.assertTemplateUsed(response, "shop/product-update.html")
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)
        self.assertEquals(self.product.name, updated_product_data["name"])
        self.assertEquals(self.product.description, updated_product_data["description"])
        self.assertEquals(self.product.unit, updated_product_data["unit"])
        self.assertEquals(self.product.unit_price, updated_product_data["unit_price"])
        self.assertEquals(self.product.in_stock, updated_product_data["in_stock"])
        self.assertEquals(self.product.sold, updated_product_data["sold"])
        self.assertEquals(self.product.is_active, updated_product_data["is_active"])
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(Image.objects.first().product, self.product)

    # @tag('x')
    def test_product_delete_POST(self):
        response = self.client.post(self.product_delete_url)

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEquals(Product.objects.count(), 0)

    # @tag('x')
    def test_product_category_filtered_GET(self):
        response = self.client.get(
            path=self.product_category_filtered_url, data={"category": self.category.id}
        )

        ic(response.context["products"])

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/home.html")
        self.assertIn("products", response.context)
        self.assertEquals(len(response.context["products"]), 1)

    # @tag('x')
    def test_provide_name_to_search_receive_results_GET(self):
        name_to_search = "test_product"
        response = self.client.get(
            path=self.search_result_url, data={"SearchByName": name_to_search}
        )

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/home.html")
        self.assertIn("products", response.context)
        self.assertEquals(len(response.context["products"]), 1)
        self.assertEquals(response.context["products"][0].name, name_to_search)

    # @tag('x')
    def test_provide_description_to_search_receive_results_GET(self):
        desc_to_search = "test_description"
        response = self.client.get(
            path=self.search_result_url, data={"SearchByName": desc_to_search}
        )

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/home.html")
        self.assertIn("products", response.context)
        self.assertEquals(len(response.context["products"]), 1)
        self.assertEquals(response.context["products"][0].description, desc_to_search)
