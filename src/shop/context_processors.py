from .models import Category


def categories_processor(request):
    categories = ["All products"] + list(Category.objects.filter(parent__isnull=True))
    context = {
        "categories": categories,
    }
    return context
