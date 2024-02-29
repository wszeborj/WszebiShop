from django.contrib import admin

from .models import Address, OrderItem, ShippingType

admin.site.register(Address)
admin.site.register(OrderItem)
admin.site.register(ShippingType)
