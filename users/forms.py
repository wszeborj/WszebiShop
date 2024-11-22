from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Account


class UserRegisterForm(UserCreationForm):
    birth_date = forms.DateField(widget=DatePickerInput(format="%Y-%m-%d"))

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # self.fields["birth_date"].widget = DatePickerInput(format="%Y-%m-%d")

    class Meta:
        model = Account
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "birth_date",
            "phone",
            "password1",
            "password2",
        ]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            "username",
            "email",
            "phone",
        )

    # def __init__(self, *args, **kwargs):
    #     super(ProfileUpdateForm, self).__init__(*args, **kwargs)
    #
    #     if 'instance' in kwargs:
    #         instance = kwargs['instance']
    #         self.fields['username'].initial = instance.first_name
    #         self.fields['email'].initial = instance.first_name
    #         self.fields['phone'].initial = instance.first_name
