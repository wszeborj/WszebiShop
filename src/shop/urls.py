from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.AllProductListView.as_view(), name="all-product-list"),
    path(
        "category-products/",
        views.ProductCategoryFileteredView.as_view(),
        name="category-filtered-products",
    ),
    path("products/", views.ProductListView.as_view(), name="user-product-list"),
    path(
        "products/<int:pk>/", views.ProductDetailsView.as_view(), name="product-details"
    ),
    path("products/create", views.ProductCreateView.as_view(), name="product-create"),
    path(
        "product/<int:pk>/update/",
        views.UpdateProductView.as_view(),
        name="product-update",
    ),
    path(
        "product/<int:pk>/delete/",
        views.DeleteProductView.as_view(),
        name="product-delete",
    ),
]
