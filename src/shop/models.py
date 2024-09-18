from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from PIL import Image as PilImage

from users.models import Account


class Category(models.Model):
    name = models.CharField(max_length=50, help_text="Name of the product category.")
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Description of the product category.",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

    def get_absolute_url(self):
        return reverse("category_list", args=[self.pk])


class Product(models.Model):
    name = models.CharField(max_length=50, help_text="Name of the product.")
    description = models.CharField(
        max_length=255, help_text="Description of the product."
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        help_text="Category to which the product belongs.",
    )
    unit = models.CharField(
        max_length=10,
        help_text="Unit of measurement for the product (e.g., kg, piece).",
    )
    unit_price = models.DecimalField(
        default=0.00,
        decimal_places=2,
        max_digits=100,
        help_text="Unit price of the product.",
    )
    in_stock = models.IntegerField(
        help_text="Quantity of the product available in stock."
    )
    sold = models.IntegerField(default=0, help_text="Number of units sold.")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the product was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Time when the product was last updated."
    )
    special_offer = models.BooleanField(
        default=False, help_text="Is the product on special offer?"
    )
    is_active = models.BooleanField(
        default=True, help_text="Is the product active and visible?"
    )
    seller = models.ForeignKey(
        Account, on_delete=models.CASCADE, help_text="User account of the seller."
    )

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

    def get_thumbnail(self):
        if self.images.filter(thumbnail=True):
            return self.images.filter(thumbnail=True).first().image
        else:
            return None


class Image(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        help_text="Product associated with the image.",
    )
    image = models.ImageField(
        upload_to="product_images", help_text="Image of the product."
    )
    thumbnail = models.BooleanField(
        default=False, help_text="Is this image the thumbnail for the product?"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the image was created."
    )

    def save(self, *args, **kwargs):
        if not self.product.images.filter(thumbnail=True).exists():
            self.thumbnail = True

            img = PilImage.open(self.image)
            if img.height > 500 or img.width > 333:
                output_size = (500, 333)
                img.thumbnail(output_size)
                thumb_io = BytesIO()
                img.save(thumb_io, format="png")
                self.image.save(
                    self.image.name, ContentFile(thumb_io.getvalue()), save=False
                )
            else:
                self.thumbnail = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"({self.id}) {self.image} created at: {self.created_at}"
