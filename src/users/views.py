from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import FormView, UpdateView, View

from .forms import ProfileUpdateForm, UserRegisterForm
from .models import Account


class RegisterFormView(FormView):
    template_name = "users/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        account = form.save(commit=False)
        account.is_active = False
        account.save()

        current_site = get_current_site(self.request)
        subject = "Activation link to your account on Wszebishop"
        message = render_to_string(
            template_name="users/account_activation_email.html",
            context={
                "account": account,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(account.pk)),
                "token": default_token_generator.make_token(account),
            },
        )
        recipient_mail = form.cleaned_data.get("email")
        send_mail(
            subject=subject,
            message=message,
            from_email="no_reply@wszebiszop.pl",
            recipient_list=[recipient_mail],
            fail_silently=False,
        )

        messages.success(
            self.request,
            f"Dear {account.username}, please confirm your email address to complete registration",
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(
            self.request,
            "Something went wrong! Check your email and try again.",
        )
        return super().form_invalid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "users/profile.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("users:profile-update")
    # queryset = Account.objects.all()

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated!")
        return super().form_valid(form)


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            account = Account.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
            account = None

        if account is not None and default_token_generator.check_token(
            user=account, token=token
        ):
            account.is_active = True
            account.save()
            messages.success(request, "Your account has been activated successfully!")
            return redirect("users:login")
        else:
            messages.warning(request, "Activation link is invalid!")
            return redirect("home")
