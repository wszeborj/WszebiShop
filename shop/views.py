import django_filters
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
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
from .models import Category, Product


class AllProductListView(ListView):
    template_name = "shop/home.html"
    model = Product
    context_object_name = "products"
    ordering = ["-created_at"]

    def get_queryset(self) -> QuerySet[Product]:
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True).prefetch_related("images")
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
        images = self.request.FILES.getlist("image")

        for image_file in images:
            image_form = ImageForm(files={"image": image_file})
            if not image_form.is_valid():
                messages.warning(
                    self.request, "Image too small, please select a larger image"
                )
                return self.form_invalid(form)

        product.save()
        for image_file in images:
            image_form = ImageForm(files={"image": image_file})
            image = image_form.save(commit=False)
            image.product = product
            image.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class UpdateProductView(LoginRequiredMixin, UpdateView):
    template_name = "shop/product-update.html"
    form_class = ProductForm
    model = Product
    success_url = reverse_lazy("shop:user-product-list")

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        images = self.request.FILES.getlist("image")

        for image_file in images:
            image_form = ImageForm(files={"image": image_file})
            if not image_form.is_valid():
                messages.warning(
                    self.request, "Image too small, please select a larger image"
                )
                return self.form_invalid(form)

        with transaction.atomic():
            product = form.save(commit=False)
            product.save()

            if images:
                product.images.all().delete()

                for image_file in images:
                    image_form = ImageForm(files={"image": image_file})
                    if image_form.is_valid():
                        image = image_form.save(commit=False)
                        image.product = product
                        image.save()

        return super().form_valid(form)


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


class ProductCategoryFilteredView(FilterView):
    template_name = "shop/home.html"
    model = Product
    context_object_name = "products"
    filterset_class = CategoriesFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.request.GET.get("category")
        if category_id:
            context["selected_category"] = get_object_or_404(Category, pk=category_id)
        else:
            context["selected_category"] = None
        return context


class SearchResultView(ListView):
    template_name = "shop/home.html"
    model = Product
    context_object_name = "products"

    def get_queryset(self):
        query = self.request.GET.get("SearchByName")
        products_list = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        return products_list
