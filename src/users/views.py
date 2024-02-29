from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView

from .forms import ProfileUpdateForm, UserRegisterForm


class RegisterFormView(FormView):
    template_name = "users/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("/login/")

    def form_vaild(self, form):
        account = form.save()

        messages.success(
            self.request,
            f"Dear {account.username}, you have been successfully signed up!",
        )

        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "users/profile.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated!")
        return super().form_valid(form)
