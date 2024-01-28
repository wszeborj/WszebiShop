from django.contrib import admin
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.AllProductListView.as_view(), name='all_product_list'), # products
    path('products/<int:pk>/', views.ProductDetailsView.as_view(), name='product_details'), # products
]
