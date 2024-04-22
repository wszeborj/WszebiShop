from django import forms

from .models import Image, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["seller"]


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["image"]
