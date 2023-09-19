from django.shortcuts import render
from django.http import HttpResponse

def shop_main(request):
    return render(request, 'shop/index.html',)
