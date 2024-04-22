from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

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
        for image in images:
            image_form = ImageForm()
            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.product = product
                image.save()
        return super().form_valid(form)


class UpdateProductView(UpdateView):
    pass
