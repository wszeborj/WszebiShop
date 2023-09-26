from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='home'),
    path('products/<int:product_id>/', views.ProductDetailsView.as_view(), name='product_details'),
]
