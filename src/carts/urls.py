from django.urls import path

from . import views

app_name = "carts"

urlpatterns = [
    path("", views.CartListView.as_view(), name="cart-details"),
    path("<int:product_id>/add/", views.AddToCart.as_view(), name="add-to-cart"),
    path(
        "<int:product_id>/remove/",
        views.RemoveFromCart.as_view(),
        name="remove-from-cart",
    ),
    path("remove-all/", views.RemoveAll.as_view(), name="remove-all"),
    path(
        "<int:cart_item_id>/removeitem/", views.RemoveItem.as_view(), name="remove-item"
    ),
    path(
        "<int:product_id>/update/", views.UpdateCart.as_view(), name="update-quantity"
    ),
]
