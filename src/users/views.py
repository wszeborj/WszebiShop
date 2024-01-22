from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from shop.models import Address
from django.views import View
from phonenumber_field.modelfields import PhoneNumberField


class Register(View):

    def get(self, request):
        form1 = UserRegisterForm()
        return render(request, 'users/register.html', {"form1": form1})

    def post(self, request):
        form1 = UserRegisterForm(request.POST)

        if form1.is_valid():
            account = form1.save()
            birth_date = form1.cleaned_data.get("birth_date")
            phone = form1.cleaned_data.get("phone")

            messages.success(request, f"Dear {account.username}, you have been successfully signed up!")
            return redirect("login")
        elif not form1.is_valid():
            print(form1.errors)
        else:
            form1 = UserRegisterForm()

        return render(request, "users/register.html", {"form1": form1})


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


