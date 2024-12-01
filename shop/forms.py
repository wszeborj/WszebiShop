from django import forms

from .models import Image, Product


class ProductForm(forms.ModelForm):
    # noinspection PyPackageRequirements
    class Meta:
        model = Product
        fields = "__all__"
        exclude = ["seller"]
        widgets = {"description": forms.Textarea(attrs={"cols": 80, "rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.help_text = None


def validate_image(image):
    try:
        width, height = image.image.size
        if width < 333 or height < 500:
            raise forms.ValidationError(f"{width}x{height} is too small")
    except Exception as e:
        raise forms.ValidationError(f"An error occurred when processing the image: {e}")


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label="image", required=False, validators=[validate_image])

    class Meta:
        model = Image
        fields = ["image"]
