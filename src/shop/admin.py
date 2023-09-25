from django.contrib import admin
from .models import Product, Category, Account, Image, Address

admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Image)
admin.site.register(Address)