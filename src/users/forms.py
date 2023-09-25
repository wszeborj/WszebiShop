from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import User
from .models import Account
from phonenumber_field.modelfields import PhoneNumberField
from bootstrap_datepicker_plus.widgets import DatePickerInput


class UserRegisterForm(UserCreationForm):
    birth_date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'))

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['birth_date'].widget = DatePickerInput(format='%Y-%m-%d')

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'birth_date', 'phone', 'password1', 'password2']



class UserRegisterForm2(forms.ModelForm):
    first_name2 = forms.CharField()
    last_name2 = forms.CharField()
    street = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    zip_code = forms.CharField()
    country = forms.CharField()
    phone = PhoneNumberField(region="PL")

    class Meta:
        model = Account
        fields = ['first_name2', 'last_name2', 'street', 'city', 'state', 'zip_code',
                  'country', 'phone']


#
# class UserRegisterForm(UserCreationForm):
#     birth_date = forms.DateField(widget=DatePickerInput(format='%Y-%m-%d'))
#     first_name2 = forms.CharField()
#     last_name2 = forms.CharField()
#     street = forms.CharField()
#     city = forms.CharField()
#     state = forms.CharField()
#     zip_code = forms.CharField()
#     country = forms.CharField()
#     phone = PhoneNumberField(region="PL")
#
#     def __init__(self, *args, **kwargs):
#         super(UserRegisterForm, self).__init__(*args, **kwargs)
#         self.fields['birth_date'].widget = DatePickerInput(format='%Y-%m-%d')
#
#     class Meta:
#         model = Account
#         fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'birth_date',
#                   'first_name2', 'last_name2', 'street', 'city', 'state', 'zip_code',
#                   'country', 'phone']



class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

#
class ProfileUpdateForm(forms.ModelForm):
    pass
    # class Meta:
    #     model = Account
    #     fields = ['image']

