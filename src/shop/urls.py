from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.AllProductListView.as_view(), name="all-product-list"),
    path(
        "products/<int:pk>/", views.ProductDetailsView.as_view(), name="product-details"
    ),
    path("products/create", views.ProductCreateView.as_view(), name="product-create"),
]
