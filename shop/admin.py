from django.contrib import admin

from .models import Category, Image, Product

# , Address


class ProductImagesInline(admin.StackedInline):
    model = Image


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category_id",
        "unit",
        "unit_price",
        "in_stock",
        "sold",
        "created_at",
        "updated_at",
        "special_offer",
    ]
    list_filter = ["category_id", "in_stock", "is_active"]
    list_editable = ["unit_price", "in_stock"]
    inlines = [ProductImagesInline]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = [
        "image",
        "created_at",
    ]
    list_filter = [
        "created_at",
    ]
