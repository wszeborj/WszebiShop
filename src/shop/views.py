import django_filters
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_filters.views import FilterView

from .forms import ImageForm, ProductForm
from .models import Product


class AllProductListView(ListView):
    template_name = "shop/home.html"
    model = Product
    context_object_name = "products"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        # for product in queryset:
        #     if product.images.exists():
        #         product.first_image = product.images.first().image
        return queryset


class ProductDetailsView(DetailView):
    template_name = "shop/product-details.html"
    model = Product
    context_object_name = "product_details"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["images"] = self.object.images.all()
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "shop/product-create.html"
    success_url = reverse_lazy("shop:all-product-list")

    def form_valid(self, form):
        product = form.save(commit=False)
        product.seller = self.request.user
        product.save()

        images = self.request.FILES.getlist("image")
        for image_file in images:
            image_form = ImageForm(files={"image": image_file})
            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.product = product
                image.save()
        return super().form_valid(form)


class UpdateProductView(LoginRequiredMixin, UpdateView):
    template_name = "shop/product-update.html"
    form_class = ProductForm
    model = Product
    success_url = reverse_lazy("shop:user-product-list")

    # def get_object(self, queryset=None):
    #     return get_object_or_404(Product, pk=self.kwargs.get('pk'))
    #
    # def get_initial(self):
    #     initial = super(UpdateProductView, self).get_initial()
    #
    #     obj = self.get_object()
    #     initial['name'] = obj.name
    #
    #     return initial


class DeleteProductView(LoginRequiredMixin, DeleteView):
    template_name = "shop/product-confirm-delete.html"
    model = Product
    success_url = reverse_lazy("shop:user-product-list")


class ProductListView(ListView):
    template_name = "shop/product-list.html"
    model = Product
    context_object_name = "product"
    ordering = ["-created_at"]

    def get_queryset(self):
        context = Product.objects.filter(seller=self.request.user)
        return context


class CategoriesFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            "category": ["exact"],
        }


class ProductCategoryFileteredView(FilterView):
    template_name = "shop/home.html"
    model = Product
    context_object_name = "products"
    filterset_class = CategoriesFilter
