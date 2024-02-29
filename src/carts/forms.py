from django import forms
from django.shortcuts import get_object_or_404

from .models import Product


class CartUpdateForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=0)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        product_id = self.cleaned_data["product_id"]
        product = get_object_or_404(Product, pk=product_id)
        if quantity > product.in_stock:
            raise forms.ValidationError(f"Only {product.in_stock} items available.")
