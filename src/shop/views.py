from django.views.generic import ListView, DetailView
from .models import Product


class AllProductListView(ListView):
    template_name = 'shop/home.html'
    model = Product
    context_object_name = 'products'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        for product in queryset:
            if product.images.exists():
                product.first_image = product.images.first().image
        return queryset


class ProductDetailsView(DetailView):
    template_name = 'shop/product-details.html'
    model = Product
    context_object_name = 'product_details'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        return context
