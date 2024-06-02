from django import forms
from PIL import Image as PilImage

from .models import Image, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        # exclude = ["seller"]
        # widgets = {"description": forms.Textarea(attrs={"cols": 80, "rows": 5})}

    # def __init__(self, *args, **kwargs):
    #     super(ProductForm, self).__init__(*args, **kwargs)
    #
    #     if 'instance' in kwargs:
    #         instance = kwargs['instance']
    #         self.fields['name'].initial = instance.name
    #


def validate_image(image):
    print("validate_image")
    try:
        img = PilImage.open(image)
        width, height = img.size
        if width < 333 or height < 500:
            raise forms.ValidationError(f"{width}x{height} is too small")
    except Exception as e:
        raise forms.ValidationError(f"An error occurred when processing the image: {e}")


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label="image", required=False, validators=[validate_image])

    class Meta:
        model = Image
        fields = ["image"]
