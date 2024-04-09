import stripe
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

from carts.models import CartItem
from orders.models import Address, Order, OrderItem, ShippingType
from shop.models import Product
from users.models import Account

from .models import Payment

YOUR_DOMAIN = "https://wszebishop.pl"


class CreateStripeCheckoutSessionView(View, LoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        # full_user_name = f"{self.request.user.first_name} {self.request.user.last_name}"
        account = self.request.user.id
        address = request.POST.get("selected_shipping_address")
        shipping_type = request.POST.get("selected_shipping_type")
        total_price_with_shipping = float(
            self.request.POST.get("total_price_with_shipping")
        )
        total_price_for_checkout = str(round(float(total_price_with_shipping) * 100))

        order_id = OrderClassProcessing.create_order(
            account=account,
            address=address,
            shipping_type=shipping_type,
            total_price_with_shipping=total_price_with_shipping,
        )

        domain = "https://YOUR_DOMAIN.pl"
        if settings.DEBUG:
            domain = "http://127.0.0.1:8000"
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=self.request.user.email,
                # customer_name=full_user_name,
                payment_method_types=["card"],
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": "pln",
                            "unit_amount": total_price_for_checkout,
                            "product_data": {"name": "t-shirt", "description": "xyz"},
                        },
                        "quantity": 1,
                    }
                ],
                success_url=domain + "/payments/success/",
                cancel_url=domain + "/payments/cancel",
                metadata={
                    "account": account,
                    "address": address,
                    "shipping_type": shipping_type,
                    "total_price_with_shipping": total_price_with_shipping,
                    "order_id": order_id,
                    "payment_type": "one-time",
                },
            )
        except Exception as e:
            print(str(e))

        return redirect(checkout_session.url, code=303)


class SuccessView(TemplateView):
    template_name = "payments/payment_success.html"


class CancelledView(TemplateView):
    template_name = "payments/payment_cancel.html"


@csrf_exempt
def stripe_webhook(request):
    print("CHECK")
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # checkout_metadata = event['data']['object']['metadata']
    # print(event['data']['object'])
    # account = Account.objects.get(pk=int(checkout_metadata.get('account')))
    # address = Address.objects.get(pk=int(checkout_metadata.get('address')))
    # shipping_type = ShippingType.objects.get(pk=int(checkout_metadata.get('shipping_type')))
    # total_price_with_shipping = int(checkout_metadata.get('total_price_with_shipping')) / 100
    #
    # order_id = OrderClassProcessing.create_order(
    #     account=account,
    #     address=address,
    #     shipping_type=shipping_type,
    #     total_price_with_shipping=total_price_with_shipping)

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = int(session["metadata"].order_id)
        # Save an order in your database, marked as 'awaiting payment'
        OrderClassProcessing.change_payment_status(
            order_id=order_id, status=Order.OrderStatus.AWAITING_PAYMENT
        )
        print("checkout session completed")

        # Check if the order is already paid (for example, from a card payment)
        #
        # A delayed notification payment will have an `unpaid` status, as
        # you're still waiting for funds to be transferred from the customer's
        # account.
        if session.payment_status == "paid":
            # Fulfill the purchase
            print("session.payment_status paid")
            order_id = int(session["metadata"].order_id)
            OrderClassProcessing.change_payment_status(
                order_id=order_id, status=Order.OrderStatus.PAID
            )
            OrderClassProcessing.fulfill_order(order_id)

    elif event["type"] == "checkout.session.async_payment_succeeded":
        session = event["data"]["object"]
        print("checkout.session.async_payment_succeeded")
        # Fulfill the purchase
        order_id = int(session["metadata"].order_id)
        OrderClassProcessing.change_payment_status(
            order_id=order_id, status=Order.OrderStatus.PAID
        )
        OrderClassProcessing.fulfill_order(order_id=order_id)

    elif event["type"] == "checkout.session.async_payment_failed":
        session = event["data"]["object"]
        print("checkout.session.async_payment_failed")
        # Send an email to the customer asking them to retry their order
        order_id = int(session["metadata"].order_id)
        OrderClassProcessing.change_payment_status(
            order_id=order_id, status=Order.OrderStatus.UNPAID
        )
        OrderClassProcessing.email_customer_about_failed_payment(
            order_id=order_id, send_email=False, save_to_file=True
        )

        # Passed signature verification
    return HttpResponse(status=200)


class OrderClassProcessing:
    @staticmethod
    def fulfill_order(order_id: int):
        # TODO: fill me in
        print("Fulfilling order")

        order = Order.objects.get(pk=order_id)
        cart_items = CartItem.objects.filter(account=order.buyer)
        for item in cart_items:
            OrderItem.objects.create(
                product=item.product,
                quantity=item.quantity,
                account=order.buyer,
                order=order,
            )

            purchased_product = Product.objects.get(pk=item.product.id)
            purchased_product.in_stock = purchased_product.in_stock - item.quantity

            item.delete()
        order = Order.objects.get(pk=order_id)
        order.OrderStatus = Order.OrderStatus.PAID

    @staticmethod
    def create_order(
        account: int, address: int, shipping_type: int, total_price_with_shipping: float
    ):
        print("Creating order")
        buyer = Account.objects.get(pk=account)
        address = Address.objects.get(pk=address)
        shipping_type = ShippingType.objects.get(pk=shipping_type)

        order = Order.objects.create(
            status=Order.OrderStatus.NEW,
            buyer=buyer,
            address=address,
            shipping_type=shipping_type,
            total_price_with_shipping=total_price_with_shipping,
        )
        order.save()

        return order.id

    @staticmethod
    def change_payment_status(order_id: int, status: Order.OrderStatus):
        print(f"change {order_id=} to {status}")
        order = Order.objects.get(pk=order_id)
        order.status = status
        order.save()

    @staticmethod
    def create_payment(order, session):
        print("create payment")
        Payment.objects.create(
            user=order.buyer,
            price=order.total_price_with_shipping,
            order=order,
            state=Payment.State.PAID,
        )

    @staticmethod
    def email_customer_about_failed_payment(
        order_id: int, send_email: bool = True, save_to_file: bool = False
    ):
        # TODO: fill me in
        print("Emailing customer")

        subject = "Problem z płatnością za Twoje zamówienie"
        message = f"""
        Hello,

        Unfortunately, the payment for your order number {order_id} was not processed.
        Please make your payment again so that we can process your order.

        Thank you,
        Wszebishop.pl
        """

        if save_to_file:
            with open(f"failed_payment_email_{order_id}.txt", "w") as file:
                file.write(f"Subject: {subject}\n\n")
                file.write(message)
            print(
                f"Email about failed payment saved to file failed_payment_email_{order_id}.txt"
            )

        if send_email:
            pass
