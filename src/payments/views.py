# import stripe
# from django.conf import settings
# from django.shortcuts import redirect, render
# from django.views import View
#
# class CreateStripeCheckoutSessionView(View):
#     def post(self, request, *args, **kwargs):
#         price = self.request.session.get("total_price_with_shipping")
#         domain = "https://wszebishop.pl"
#         if settings.DEBUG:
#             domain = "http://127.0.0.1:8000"
#
#         try:
#             checkout_session = stripe.checkout.Session.create(
#                 line_items=[
#                     {
#                         "price": price,
#                         "currency": "PLN",
#                         "description": "order_id",
#                     }
#                 ],
#                 mode="payment",
#                 success_url=YOUR_DOMAIN + "/success.html",
#                 cancel_url=YOUR_DOMAIN + "/cancel.html",
#             )
#         except Exception as e:
#             return str(e)
#
#         return redirect(checkout_session.url, code=303)
