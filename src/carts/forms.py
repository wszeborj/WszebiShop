from django import forms
from shop.models import Product

class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=0, max_value=Product.in_stock)