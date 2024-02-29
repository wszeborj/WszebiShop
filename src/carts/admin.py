from django.contrib import admin

from .models import CartItem


@admin.register(CartItem)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "quantity",
    ]
    list_filter = ["product", "quantity"]
    list_editable = [
        "quantity",
    ]
