from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase
from icecream import ic

from shop.models import Image, Product
from users.factories import AccountFactory

from ..factories import CategoryFactory, ProductFactory, create_image


class TestProductView(TestCase):
    def setUp(self):
        self.product = ProductFactory.create(name="test_product")

    def test_all_product_list_view_GET(self):
        all_product_list_url = reverse(viewname="shop:all-product-list")
        response = self.client.get(all_product_list_url)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/home.html")

    def test_product_details_view_GET(self):
        product_detail_url = reverse(
            viewname="shop:product-details", args=[self.product.id]
        )
        response = self.client.get(product_detail_url)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/product-details.html")


class TestProductCreateView(TestCase):
    def setUp(self):
        self.account = AccountFactory.create(
            username="test_user", password="Test.Password"
        )
        self.category = CategoryFactory.create(name="test_category1")

        self.client.force_login(self.account)

        self.product_create_url = reverse("shop:product-create")

        self.product_data = {
            "name": "test_product1",
            "description": "test_description2",
            "category": self.category.id,
            "unit": "test_unit",
            "unit_price": 100.00,
            "in_stock": 100,
            "sold": 0,
            "is_active": True,
            "seller": self.account.id,
        }

    def test_product_create_view_no_image_not_logged_should_not_create_product_POST(
        self,
    ):
        self.client.logout()

        response = self.client.post(self.product_create_url, self.product_data)

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEquals(Product.objects.count(), 0)

    def test_product_create_no_data_should_not_create_new_product_POST(self):
        empty_product_data = {}
        response = self.client.post(self.product_create_url, empty_product_data)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 0)

    def test_product_create_view_no_image_should_create_product_POST(self):
        response = self.client.post(self.product_create_url, self.product_data)

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEquals(Product.objects.count(), 1)
        self.assertEquals(Product.objects.first().name, "test_product1")

    def test_product_create_with_valid_image_POST(self):
        image = create_image()
        image_file = SimpleUploadedFile(
            name="test.png", content=image.read(), content_type="image/png"
        )
        self.product_data["image"] = [image_file]

        response = self.client.post(
            self.product_create_url,
            data=self.product_data,
            format="multipart/form-data",
        )

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEquals(Product.objects.count(), 1)
        self.assertEquals(Product.objects.first().name, self.product_data["name"])
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(Image.objects.first().product.name, self.product_data["name"])

    def test_product_create_view_with_invalid_image_should_not_create_new_object_POST(
        self,
    ):
        image = create_image(width=50, height=50)
        image_file = SimpleUploadedFile(
            name="test.png", content=image.read(), content_type="image/png"
        )
        self.product_data["image"] = [image_file]

        response = self.client.post(
            path=self.product_create_url, data=self.product_data, follow=True
        )

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 0)


class TestProductUpdateDeleteSearchView(TestCase):
    def setUp(self):
        self.account = AccountFactory.create(
            username="test_user", password="Test.Password"
        )
        self.category = CategoryFactory.create(name="test_category1")
        self.product = ProductFactory.create(
            name="test_product1",
            description="test_description",
            category=self.category,
            unit="test_unit",
            unit_price=200.00,
            in_stock=200,
            sold=0,
            is_active=True,
            seller=self.account,
        )

        self.updated_product_data = {
            "name": "updated_product",
            "description": "updated_test_description",
            "category": self.category.id,
            "unit": "upd_unit",
            "unit_price": 300.00,
            "in_stock": 300,
            "sold": 1,
            "is_active": False,
        }

        self.client.force_login(self.account)

        self.product_update_url = reverse("shop:product-update", args=[self.product.id])
        self.product_delete_url = reverse("shop:product-delete", args=[self.product.id])
        self.product_category_filtered_url = reverse("shop:category-filtered-products")
        self.search_result_url = reverse("shop:search-results")

    def test_product_update_no_image_POST(self):
        response = self.client.post(
            path=self.product_update_url, data=self.updated_product_data, follow=True
        )
        self.product.refresh_from_db()

        self.assertTemplateUsed(response, "shop/product-list.html")
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)
        self.assertEquals(self.product.name, self.updated_product_data["name"])
        self.assertEquals(
            self.product.description, self.updated_product_data["description"]
        )
        self.assertEquals(self.product.unit, self.updated_product_data["unit"])
        self.assertEquals(
            self.product.unit_price, self.updated_product_data["unit_price"]
        )
        self.assertEquals(self.product.in_stock, self.updated_product_data["in_stock"])
        self.assertEquals(self.product.sold, self.updated_product_data["sold"])
        self.assertEquals(
            self.product.is_active, self.updated_product_data["is_active"]
        )

    def test_product_update_with_valid_image_POST(self):
        image = create_image()
        image_file = SimpleUploadedFile(
            name="updated_test.png", content=image.read(), content_type="image/png"
        )

        self.updated_product_data["image"] = image_file
        ic(self.updated_product_data["image"])

        response = self.client.post(
            path=self.product_update_url, data=self.updated_product_data, follow=True
        )

        if response.context and "form" in response.context:
            ic(response.context["form"].errors)
        else:
            ic("No error")
        self.product.refresh_from_db()
        # self.assertTemplateUsed(response, "shop/product-update.html")
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)
        self.assertEquals(self.product.name, self.updated_product_data["name"])
        self.assertEquals(
            self.product.description, self.updated_product_data["description"]
        )
        self.assertEquals(self.product.unit, self.updated_product_data["unit"])
        self.assertEquals(
            self.product.unit_price, self.updated_product_data["unit_price"]
        )
        self.assertEquals(self.product.in_stock, self.updated_product_data["in_stock"])
        self.assertEquals(self.product.sold, self.updated_product_data["sold"])
        self.assertEquals(
            self.product.is_active, self.updated_product_data["is_active"]
        )
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(Image.objects.first().product, self.product)

    def test_product_update_view_not_logged_should_not_update_product_POST(self):
        self.client.logout()

        response = self.client.post(
            path=self.product_update_url, data=self.updated_product_data, follow=True
        )
        # self.assertEquals(response.status_code, HTTPStatus.FOUND)

        self.assertEquals(Product.objects.count(), 1)
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)
        self.assertNotEquals(self.product.name, self.updated_product_data["name"])
        self.assertNotEquals(
            self.product.description, self.updated_product_data["description"]
        )
        self.assertNotEquals(self.product.unit, self.updated_product_data["unit"])
        self.assertNotEquals(
            self.product.unit_price, self.updated_product_data["unit_price"]
        )
        self.assertNotEquals(
            self.product.in_stock, self.updated_product_data["in_stock"]
        )
        self.assertNotEquals(self.product.sold, self.updated_product_data["sold"])
        self.assertNotEquals(
            self.product.is_active, self.updated_product_data["is_active"]
        )

        expected_url = f"{reverse('users:login')}?next={self.product_update_url}"
        self.assertRedirects(response, expected_url)

    def test_product_delete_POST(self):
        response = self.client.post(self.product_delete_url)

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEquals(Product.objects.count(), 0)

    def test_product_delete_view_not_logged_should_not_delete_product_POST(self):
        self.client.logout()

        response = self.client.post(
            path=self.product_delete_url, data=self.updated_product_data, follow=True
        )
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(Product.objects.count(), 1)
        expected_url = f"{reverse('users:login')}?next={self.product_delete_url}"
        self.assertRedirects(response, expected_url)

    def test_product_category_filtered_GET(self):
        response = self.client.get(
            path=self.product_category_filtered_url, data={"category": self.category.id}
        )

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/home.html")
        self.assertIn("products", response.context)
        self.assertEquals(len(response.context["products"]), 1)

    def test_provide_name_to_search_receive_results_GET(self):
        name_to_search = "test_product"
        response = self.client.get(
            path=self.search_result_url, data={"SearchByName": name_to_search}
        )

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "shop/home.html")
        self.assertIn("products", response.context)
        self.assertEquals(len(response.context["products"]), 1)

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
