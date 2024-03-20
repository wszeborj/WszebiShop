from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.OrderListView.as_view(), name="order"),
    path(
        "<int:product_id>/product-to-order/",
        views.ProductToOrder.as_view(),
        name="product-to-order",
    ),
    path("add-address", views.AddAddress.as_view(), name="add-address"),
    # path("select-shipping-address", views.SelectShippingAddress.as_view(), name="select-shipping-address"),
    # path("select-shipping-type", views.SelectShippingType.as_view(), name="select-shipping-type"),
]
