from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Product, Image, Category
from django.views.generic import DetailView


class CategoryListView(View):
    model = Category
    template_name = 'sidebar.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True)


class AllProductListView(View): #listview
    template_name = 'shop/home.html'

    def get(self, request):
        latest_products = Product.objects.order_by('-created_at')[:3]
        # featured_products = Product.objects.all()

        for product in latest_products:
            product.first_image = product.images.first().image if product.images.exists() else None

        context = {
            'products': latest_products,
        }

        return render(request, self.template_name, context)


class ProductDetailsView(View):
    template_name = 'shop/product_details.html'

    def get(self, request, pk):

        product_details = get_object_or_404(Product, pk=pk)
        images = product_details.images.all()

        context = {
            'product_details': product_details,
            'images': images,

        }

        return render(request, self.template_name, context)
