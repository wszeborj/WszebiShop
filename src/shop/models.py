from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import Account


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    category_id = models.ForeignKey(Category, on_delete=models.PROTECT)
    unit = models.CharField(max_length=10)
    unit_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
    quantity_in_stock = models.IntegerField()
    sold = models.IntegerField()
    date = models.DateTimeField()
    special_offer = models.BooleanField()

    def __str__(self):
        return f'{self.name} ({self.id})'


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media\\product_images')

    def __str__(self):
        return f'({self.id}) {self.image} assigned to: {self.product}'


class Address(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    phone = PhoneNumberField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=6)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class ShoppingCart(models.Model):
    product_list = models.ManyToManyField(Product, null=True, blank=True)
    customer = models.ForeignKey(Account, on_delete=models.CASCADE)


class Payment(models.Model):
    class State(models.TextChoices):
        NEW = 'NEW', 'NEW'
        PAID = 'PAID', 'PAID'

    paid = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
    paid_time = models.DateTimeField()
    state = models.IntegerField(choices=State.choices)


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        NEW = 'NEW', 'NEW'
        HOLD = 'HOLD', 'HOLD'
        SHIPPED = 'SHIPPED', 'SHIPPED'
        DELIVERED = 'DELIVERED', 'DELIVERED'
        CLOSED = 'CLOSED', 'CLOSED'

    class ShippingType(models.TextChoices):
        COURIER = 'COURIER', 'COURIER'
        COURIER_CASH_ON_DELIVERY = 'COURIER_CASH_ON_DELIVERY', 'COURIER_CASH_ON_DELIVERY'
        POST = 'POST', 'POST'
        PARCEL_LOCKER = 'PARCEL_LOCKER', 'PARCEL_LOCKER'

    shopping_cart = models.ForeignKey(ShoppingCart, on_delete=models.PROTECT)
    buyer = models.ForeignKey(Account, on_delete=models.PROTECT)
    order_date = models.DateTimeField()
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    shipping_type = models.TextField(choices=ShippingType.choices)
    total_cost = models.DecimalField(default=0.00, decimal_places=2, max_digits=100)
    order_status = models.TextField(choices=OrderStatus.choices)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)


class Company(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    company_NIP = models.IntegerField()
    company_name = models.CharField()
