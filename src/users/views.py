from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView

from phonenumber_field.modelfields import PhoneNumberField



# class Register(View): # FormView
#
#     def get(self, request):
#         form = UserRegisterForm()
#         return render(request, 'users/register.html', {"form": form})
#
#     def post(self, request):
#         form = UserRegisterForm(request.POST)
#
#         if form.is_valid():
#             account = form.save()
#             birth_date = form.cleaned_data.get("birth_date")
#             phone = form.cleaned_data.get("phone")
#
#             messages.success(request, f"Dear {account.username}, you have been successfully signed up!")
#             return redirect("login")
#         elif not form.is_valid():
#             print(form.errors)
#         else:
#             form = UserRegisterForm()
#
#         return render(request, "users/register.html", {"form": form})


class RegisterFormView(FormView):
    template_name = "users/register.html"
    form_class = UserRegisterForm
    success_url = "/login/"

    def form_vaild(self, form):
        account = form.save()
        birth_date = form.cleaned_data.get("birth_date")
        phone = form.cleaned_data.get("phone")

        messages.success(self.request, f"Dear {account.username}, you have been successfully signed up!")

        return super().form_valid(form)


# @login_required
# def profile(request): #updateview
#     if request.method == 'POST':
#         user_form = ProfileUpdateForm(request.POST, instance=request.user)
#         profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
#
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, "Your profile's been updated")
#             return redirect('profile')
#     else:
#         user_form = ProfileUpdateForm(instance=request.user)
#         profile_form = ProfileUpdateForm(instance=request.user.profile)
#
#     return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "users/profile.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('profile')
    context_object_name = 'ProfileUpdate'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ProfileUpdate'] = self.get_form()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated!')
        return super().form_valid(form)
