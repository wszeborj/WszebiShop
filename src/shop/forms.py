from django import forms

from .models import Image, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        exclude = ["seller"]
        widgets = {"description": forms.Textarea(attrs={"cols": 80, "rows": 5})}

    # def __init__(self, *args, **kwargs):
    #     super(ProductForm, self).__init__(*args, **kwargs)
    #
    #     if 'instance' in kwargs:
    #         instance = kwargs['instance']
    #         self.fields['name'].initial = instance.name
    #


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label="image", required=False)

    class Meta:
        model = Image
        fields = ["image"]
