from django.contrib import admin
from django.urls import path

from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.view_cart, name='cart-details'),
    # path('', views.CartListView.as_view(), name='cart-details'),
    # path('<int:product_id>/add/', views.add_to_cart, name='add-to-cart'),
    path('<int:product_id>/add/', views.AddToCart.as_view(), name='add-to-cart'),
    # path('<int:product_id>/remove/', views.remove_from_cart, name='remove-from-cart'),
    path('<int:product_id>/remove/', views.RemoveFromCart.as_view(), name='remove-from-cart'),
    # path('remove-all/', views.remove_all, name='remove-all'),
    path('remove-all/', views.RemoveAll.as_view(), name='remove-all'),

]