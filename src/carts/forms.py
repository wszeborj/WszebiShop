from django import forms


class CartUpdateForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=0, error_messages={"min_value": "Quantity cannot be negative"}
    )

    # TODO sprawdzić.
    def clean_quantity(self) -> int:
        quantity = self.cleaned_data["quantity"]
        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative")
        return quantity
