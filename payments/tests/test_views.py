import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import stripe
from box import Box
from django.conf import settings
from django.core import mail
from django.shortcuts import reverse
from django.test import RequestFactory, TestCase

from orders.factories import AddressFactory, OrderFactory, ShippingTypeFactory
from orders.models import Order
from users.factories import AccountFactory

from ..views import process_webhook_event, stripe_webhook


class TestWebhook(TestCase):
    def setUp(self):
        self.account = AccountFactory.create()
        self.client.force_login(self.account)

        self.address = AddressFactory.create(account=self.account)
        self.shipping_type = ShippingTypeFactory.create()
        self.order = OrderFactory.create(
            buyer=self.account,
            address=self.address,
            shipping_type=self.shipping_type,
            status=Order.OrderStatus.NEW,
        )

        self.factory = RequestFactory()

    @patch("stripe.Webhook.construct_event")
    def test_valid_webhook_with_payment_intent_succeeded(self, mock_construct_event):
        event_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "payment_status": "paid",
                    "metadata": {"order_id": self.order.id},
                }
            },
        }
        event_mock = MagicMock()
        event_mock.type = event_data["type"]
        event_mock.data["object"] = event_data["data"]["object"]
        mock_construct_event.return_value = event_mock

        request = self.factory.post(
            path="stripe/webhook",
            data=event_data,
            content_type="application/json",
        )
        request.META["HTTP_STRIPE_SIGNATURE"] = "test_signature"

        response = stripe_webhook(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch("stripe.Webhook.construct_event")
    def test_webhook_with_invalid_payload(self, mock_construct_event):
        mock_construct_event.side_effect = ValueError("Invalid payload")

        request = self.factory.post(
            path="stripe/webhook",
            data={},
            content_type="application/json",
        )
        request.META["HTTP_STRIPE_SIGNATURE"] = "test_signature"

        response = stripe_webhook(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @patch("stripe.Webhook.construct_event")
    def test_webhook_with_invalid_signature(self, mock_construct_event):
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature", "header"
        )
        event_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "payment_status": "paid",
                    "metadata": {"order_id": self.order.id},
                }
            },
        }
        event_mock = MagicMock()
        event_mock.type = event_data["type"]
        event_mock.data["object"] = event_data["data"]["object"]
        mock_construct_event.return_value = event_mock

        request = self.factory.post(
            path="stripe/webhook",
            data=event_data,
            content_type="application/json",
        )
        request.META["HTTP_STRIPE_SIGNATURE"] = "test_signature"

        response = stripe_webhook(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_invalid_signature(self, mock_construct_event):
        event_mock = MagicMock()
        event_mock.type = "checkout.session.completed"
        event_mock.data = {
            "object": {
                "payment_status": "paid",
                "metadata": {"order_id": self.order.id},
            }
        }
        mock_construct_event.return_value = event_mock
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature", "header"
        )

        payload = json.dumps({"type": "payment_intent.succeeded"})
        signature = "invalid_signature"

        request = self.factory.post(
            path="stripe/webhook",
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )
        response = stripe_webhook(request)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_proces_webhook_event_checkout_session_completed_payment_status_paid(self):
        event_mock = Box(
            {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "payment_status": "paid",
                        "metadata": {"order_id": str(self.order.id)},
                    }
                },
            }
        )

        process_webhook_event(event_mock)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.OrderStatus.PAID)

    def test_proces_webhook_event_checkout_session_async_payment_succeeded_payment_status_paid(
        self,
    ):
        event_mock = Box(
            {
                "type": "checkout.session.async_payment_succeeded",
                "data": {
                    "object": {
                        "payment_status": "paid",
                        "metadata": {"order_id": str(self.order.id)},
                    }
                },
            }
        )

        process_webhook_event(event_mock)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.OrderStatus.PAID)

    def test_proces_webhook_event_checkout_session_async_payment_failed_payment_status_unpaid(
        self,
    ):
        event_mock = Box(
            {
                "type": "checkout.session.async_payment_failed",
                "data": {
                    "object": {
                        "payment_status": "unpaid",
                        "metadata": {"order_id": str(self.order.id)},
                    }
                },
            }
        )

        process_webhook_event(event_mock)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Issue with payment for your order")

    def test_success_view(self):
        response = self.client.get(reverse("payments:payment-success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/payment_success.html")

    def test_cancelled_view(self):
        response = self.client.get(reverse("payments:payment-cancel"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/payment_cancel.html")

    def test_process_webhook_event_with_payment_intent_succeeded(self):
        self.order = OrderFactory.create(
            id=65,
            buyer=self.account,
            address=self.address,
            shipping_type=self.shipping_type,
            status=Order.OrderStatus.NEW,
        )

        payload = b'{\n  "id": "evt_1PsULo06BJRMpUupR5D4hlpn",\n  "object": "event",\n  "api_version": "2023-10-16",\n  "created": 1724784163,\n  "data": {\n    "object": {\n      "id": "cs_test_a1C52qqSaZGweHfoflOcztmd2Bp0l7wVpY26VKoJkGrCo0veznQdcMeObb",\n      "object": "checkout.session",\n      "after_expiration": null,\n      "allow_promotion_codes": null,\n      "amount_subtotal": 100753,\n      "amount_total": 100753,\n      "automatic_tax": {\n        "enabled": false,\n        "liability": null,\n        "status": null\n      },\n      "billing_address_collection": null,\n      "cancel_url": "http://127.0.0.1:8000/payments/cancel",\n      "client_reference_id": null,\n      "client_secret": null,\n      "consent": null,\n      "consent_collection": null,\n      "created": 1724784149,\n      "currency": "pln",\n      "currency_conversion": null,\n      "custom_fields": [\n\n      ],\n      "custom_text": {\n        "after_submit": null,\n        "shipping_address": null,\n        "submit": null,\n        "terms_of_service_acceptance": null\n      },\n      "customer": null,\n      "customer_creation": "if_required",\n      "customer_details": {\n        "address": {\n          "city": null,\n          "country": "PL",\n          "line1": null,\n          "line2": null,\n          "postal_code": null,\n          "state": null\n        },\n        "email": "admin@admin.com",\n        "name": "testname testsurname",\n        "phone": null,\n        "tax_exempt": "none",\n        "tax_ids": [\n\n        ]\n      },\n      "customer_email": "admin@admin.com",\n      "expires_at": 1724870549,\n      "invoice": null,\n      "invoice_creation": {\n        "enabled": false,\n        "invoice_data": {\n          "account_tax_ids": null,\n          "custom_fields": null,\n          "description": null,\n          "footer": null,\n          "issuer": null,\n          "metadata": {\n          },\n          "rendering_options": null\n        }\n      },\n      "livemode": false,\n      "locale": null,\n      "metadata": {\n        "account": "1",\n        "total_price_with_shipping": "1007.53",\n        "address": "2",\n        "order_id": "65",\n        "shipping_type": "5",\n        "payment_type": "one-time"\n      },\n      "mode": "payment",\n      "payment_intent": "pi_3PsULk06BJRMpUup1lWc8R3e",\n      "payment_link": null,\n      "payment_method_collection": "if_required",\n      "payment_method_configuration_details": null,\n      "payment_method_options": {\n        "card": {\n          "request_three_d_secure": "automatic"\n        }\n      },\n      "payment_method_types": [\n        "card"\n      ],\n      "payment_status": "paid",\n      "phone_number_collection": {\n        "enabled": false\n      },\n      "recovered_from": null,\n      "saved_payment_method_options": null,\n      "setup_intent": null,\n      "shipping_address_collection": null,\n      "shipping_cost": null,\n      "shipping_details": null,\n      "shipping_options": [\n\n      ],\n      "status": "complete",\n      "submit_type": null,\n      "subscription": null,\n      "success_url": "http://127.0.0.1:8000/payments/success/",\n      "total_details": {\n        "amount_discount": 0,\n        "amount_shipping": 0,\n        "amount_tax": 0\n      },\n      "ui_mode": "hosted",\n      "url": null\n    }\n  },\n  "livemode": false,\n  "pending_webhooks": 2,\n  "request": {\n    "id": null,\n    "idempotency_key": null\n  },\n  "type": "checkout.session.completed"\n}'
        sig_header = "t=1724784164,v1=6dea9f32f333751f384c33d2726f09d17210827c1c682efe77e971bf48ef2afb,v0=331524d6be4ce8f9792a2dc129ffb0ba3a7b94616c1dc410d26d1483d8deb956"

        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET, tolerance=10000000000
        )
        process_webhook_event(event)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.OrderStatus.PAID)
