from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path(
        "confirmation",
        views.OrderConfirmationListView.as_view(),
        name="order-confirmation",
    ),
    path(
        "<int:product_id>/product-to-order/",
        views.ProductToOrder.as_view(),
        name="product-to-order",
    ),
    path("add-address", views.AddAddress.as_view(), name="add-address"),
    path("", views.OrderListView.as_view(), name="orders-list"),
    path("sales", views.SalesListView.as_view(), name="sales-list"),
    path("<int:pk>/detail", views.OrderDetailView.as_view(), name="order-details"),
]
