from django.contrib import admin

from .models import Address, Order, OrderItem, ShippingType

admin.site.register(Address)
admin.site.register(OrderItem)
admin.site.register(ShippingType)
admin.site.register(Order)
