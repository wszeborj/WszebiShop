from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserRegisterForm2, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from shop.models import Address
from django.views import View
from phonenumber_field.modelfields import PhoneNumberField


class Register(View):

    def get(self, request):
        form1 = UserRegisterForm()
        form2 = UserRegisterForm2()
        return render(request, 'users/register.html', {"form1": form1, "form2": form2})

    def post(self, request):
        form1 = UserRegisterForm(request.POST)
        form2 = UserRegisterForm2(request.POST)
        if form1.is_valid() and form2.is_valid():
            account = form1.save()
            first_name2 = form2.cleaned_data.get("first_name2")
            last_name2 = form2.cleaned_data.get("last_name2")
            birth_date = form2.cleaned_data.get("birth_date")
            street = form2.cleaned_data.get("street")
            city = form2.cleaned_data.get("city")
            state = form2.cleaned_data.get('state')
            zip_code = form2.cleaned_data.get("zip_code")
            country = form2.cleaned_data.get("country")
            phone = form2.cleaned_data.get("phone")

            new_address = Address.objects.create(
                    account=account,
                    first_name=first_name2,
                    last_name=last_name2,
                    street=street,
                    phone=phone,
                    state=state,
                    city=city,
                    postal_code=zip_code,
                    country=country
            )

            messages.success(request, f"Dear {account.username}, you have been successfully signed up!")
            return redirect("login")
        elif not form1.is_valid() or not form2.is_valid():
            print(form1.errors)
            print(form2.errors)
        else:
            form1 = UserRegisterForm()
            form2 = UserRegisterForm2()

        return render(request, "users/register.html", {"form1": form1, "form2": form2})


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile's been updated")
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})


