from django import forms


class CartUpdateForm(forms.Form):
    quantity = forms.IntegerField(min_value=0)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative")
        return quantity
