from .models import Category


def categories_processor(request):
    categories = Category.objects.filter(parent__isnull=True)
    context = {
        'categories': categories,
    }
    return context