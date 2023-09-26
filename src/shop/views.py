from django.shortcuts import render
from django.views import View
from .models import Product, Image


class ProductListView(View):
    template_name = 'shop/index.html'

    def get(self, request):
        featured_products = Product.objects.all()

        for product in featured_products:
            product.first_image = product.images.first().image if product.images.exists() else None

        latest_products = Product.objects.order_by('-date')[:6]

        context = {
            'featured_products': featured_products,
            'latest_products': latest_products,
        }

        return render(request, self.template_name, context)

class ProductDetailsView(View):
    template_name = 'shop/product_details.html'

    def get(self, request, product_id):

        product = Product.objects.get(pk=product_id)
        images = Image.objects.filter(product=product)

        context = {
            'product': product,
            'images': images,
        }

        return render(request, self.template_name, context)

