from django import forms

from .models import Image, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["seller"]
        widgets = {"description": forms.Textarea(attrs={"cols": 80, "rows": 5})}


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label="image", required=False)

    class Meta:
        model = Image
        fields = ["image"]
