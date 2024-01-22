from django.contrib import admin
from .models import Product, Category, Image, Address


class ProductImagesInline(admin.StackedInline):
    model = Image


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', ]
    list_filter = ['parent', ]
    list_editable = ['parent', ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_id', 'unit', 'unit_price', 'quantity_in_stock', 'sold', 'created_at',
                    'updated_at', 'special_offer']
    list_filter = ['category_id', 'quantity_in_stock', 'is_active']
    list_editable = ['unit_price', 'quantity_in_stock']
    inlines = [ProductImagesInline]


# @admin.register(Image)
# class ImageAdmin(admin.ModelAdmin):
#     list_display = ['image', 'created_at',]
#     list_filter = ['created_at',]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['account', 'country', 'state', 'city', 'street',]
    list_filter = ['country', 'state', 'city', 'street',]
