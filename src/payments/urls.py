from django.urls import path

from .views import (
    CancelledView,
    CreateStripeCheckoutSessionView,
    SuccessView,
    stripe_webhook,
)

app_name = "payments"

urlpatterns = [
    path("process/", CreateStripeCheckoutSessionView.as_view(), name="payment-process"),
    path("success/", SuccessView.as_view(), name="payment-success"),
    path("cancel/", CancelledView.as_view(), name="payment-cancel"),
    path("stripe-webhook/", stripe_webhook, name="stripe-webhook"),
]
