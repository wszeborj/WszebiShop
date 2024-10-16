from .models import Category


def categories_processor(request):
    categories = ["All products"] + list(Category.objects.filter())
    context = {
        "categories": categories,
    }
    return context
