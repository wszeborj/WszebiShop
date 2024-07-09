from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from PIL import Image as PilImage

from users.models import Account


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    # todo: wyrzucic parent
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
    special_offer = models.BooleanField(default=False)
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

    def get_thumbnail(self):
        if self.images.filter(thumbnail=True):
            return self.images.filter(thumbnail=True).first().image
        else:
            return None


class Image(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="product_images")
    thumbnail = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

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
