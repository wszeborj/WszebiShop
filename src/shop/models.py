from django.db import models
from django.urls import reverse

from users.models import Account


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

    def get_absolute_url(self):
        return reverse("category_list", args=[self.parent])


class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    unit = models.CharField(max_length=10)
    unit_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
    in_stock = models.IntegerField()
    sold = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    special_offer = models.BooleanField()
    is_active = models.BooleanField(default=True)
    seller = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        verbose_name_plural = "Products"
        ordering = ("-created_at",)

    def get_absolute_url(self):
        return reverse("shop:product-details", args=[str(self.pk)])

    def first_image(self):
        if self.images.exists():
            return self.images.first().image
        else:
            return None


class Image(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="product_images", default="no_image_available.jpg"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"({self.id}) {self.image} created at: {self.created_at}"


# class Company(models.Model):
#     account = models.ForeignKey(Account, on_delete=models.CASCADE)
#     company_NIP = models.IntegerField()
#     company_name = models.CharField()
